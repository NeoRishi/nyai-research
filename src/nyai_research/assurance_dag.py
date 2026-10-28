"""Host-anchored multi-hop Assurance DAG, warrant vertex-cut independence, and causal-slice pruning.

Extends runtime_evidence.py (1-hop execution/hash binding), graph_warrants.py (lineage traversal),
and contracts.py (contestable decision records) to multi-step evaluation workflows.
"""
import ast
import hashlib
import subprocess
import sys
from pathlib import Path


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def extract_python_imports(path: Path) -> list[str]:
    try:
        tree = ast.parse(Path(path).read_text(encoding='utf-8'))
    except Exception:
        return []
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split('.')[0])
    return sorted(imports)


def inspect_semantic_slice_ast(active_files: dict[str, str]) -> list[str]:
    flags = []
    for label, source in sorted(active_files.items()):
        try:
            tree = ast.parse(source)
        except SyntaxError:
            flags.append(f'{label}:syntax_error')
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Assert):
                if isinstance(node.test, ast.Constant) and node.test.value is True:
                    flags.append(f'{label}:trivial_assert_true')
                elif isinstance(node.test, ast.Compare):
                    for comp in node.test.comparators:
                        if isinstance(comp, ast.UnaryOp) and isinstance(comp.op, ast.USub):
                            if isinstance(comp.operand, ast.Constant) and comp.operand.value >= 100:
                                flags.append(f'{label}:relaxed_threshold_hack')
            elif isinstance(node, ast.FunctionDef) and node.name == 'evaluate_candidate':
                used_names = {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}
                arg_names = {a.arg for a in node.args.args}
                if arg_names and not (arg_names & used_names):
                    flags.append(f'{label}:hardcoded_return_ignoring_inputs')
    return flags


def observe_step_execution(
    step_id: int,
    script_path: Path,
    arg_paths: list[Path],
    task_scope: str,
    cwd: Path,
) -> dict:
    read_files = [Path(script_path)] + [Path(p) for p in arg_paths]
    before_hashes = {p.name: sha256_file(p) for p in read_files if p.exists()}
    imports = extract_python_imports(script_path)
    for imp in imports:
        candidate_mod = cwd / f'{imp}.py'
        if candidate_mod.exists():
            before_hashes[candidate_mod.name] = sha256_file(candidate_mod)

    completed = subprocess.run(
        [sys.executable, str(script_path)] + [str(p) for p in arg_paths],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    after_hashes = {p.name: sha256_file(p) for p in read_files if p.exists()}
    for imp in imports:
        candidate_mod = cwd / f'{imp}.py'
        if candidate_mod.exists():
            after_hashes[candidate_mod.name] = sha256_file(candidate_mod)

    return dict(
        step_id=step_id,
        script_name=Path(script_path).name,
        arg_names=[Path(p).name for p in arg_paths],
        task_scope=task_scope,
        before_hashes=before_hashes,
        after_hashes=after_hashes,
        stable_during_run=(before_hashes == after_hashes),
        ast_imports=imports,
        exit_code=completed.returncode,
        stdout=completed.stdout.strip(),
        stderr=completed.stderr.strip(),
    )


def compute_causal_ancestors(dag_state: dict) -> dict:
    decision = dag_state['decision']
    claims = dag_state['claims']
    artifacts = dag_state['artifacts']
    observations = dag_state['observations']

    active_claim_ids = []
    queue = list(decision.get('supporting_claims', []))
    visited_claims = set()
    while queue:
        cid = queue.pop(0)
        if cid in visited_claims or cid not in claims:
            continue
        visited_claims.add(cid)
        active_claim_ids.append(cid)
        for parent_cid in claims[cid].get('upstream_claims', []):
            if parent_cid not in visited_claims:
                queue.append(parent_cid)

    active_artifact_names = set()
    active_step_ids = set()
    active_warrant_modules = set()

    for cid in active_claim_ids:
        claim = claims[cid]
        obs_id = claim.get('observation_step_id')
        if obs_id is not None and obs_id in observations:
            active_step_ids.add(obs_id)
            obs = observations[obs_id]
            active_artifact_names.update(obs['before_hashes'].keys())
            for imp in obs.get('ast_imports', []):
                if f'{imp}.py' in artifacts:
                    active_warrant_modules.add(f'{imp}.py')
                    active_artifact_names.add(f'{imp}.py')
        for art_name in claim.get('bound_artifacts', []):
            active_artifact_names.add(art_name)
            art_info = artifacts.get(art_name, {})
            if art_info.get('created_by_step') is not None:
                active_step_ids.add(art_info['created_by_step'])

    all_steps = dag_state.get('all_trajectory_steps', [])
    pruned_steps = [s for s in all_steps if s['step_id'] in active_step_ids]
    total_tokens = sum(len(s.get('log_text', '').split()) for s in all_steps) or 1
    slice_tokens = sum(len(s.get('log_text', '').split()) for s in pruned_steps)

    return dict(
        active_claim_ids=active_claim_ids,
        active_artifact_names=sorted(active_artifact_names),
        active_step_ids=sorted(active_step_ids),
        active_warrant_modules=sorted(active_warrant_modules),
        total_steps=len(all_steps),
        causal_slice_steps=len(pruned_steps),
        step_compression_ratio=round(1.0 - (len(pruned_steps) / max(len(all_steps), 1)), 4),
        token_compression_ratio=round(1.0 - (slice_tokens / total_tokens), 4),
    )


def evaluate_assurance_dag(dag_state: dict, include_stage2_semantic_slice: bool = True) -> dict:
    decision = dag_state['decision']
    claims = dag_state['claims']
    artifacts = dag_state['artifacts']
    observations = dag_state['observations']
    approval = dag_state.get('approval') or {}

    ancestors = compute_causal_ancestors(dag_state)
    active_claim_ids = ancestors['active_claim_ids']

    checks = {}
    defeated_reasons = []
    invalidating_steps = set()
    repair_targets = set()

    approval_ok = (
        bool(approval.get('active'))
        and approval.get('task_scope') == decision.get('requested_scope')
        and set(approval.get('approved_claims', [])) == set(decision.get('supporting_claims', []))
    )
    checks['approval_valid_and_scoped'] = approval_ok
    if not approval_ok:
        defeated_reasons.append('approval_missing_revoked_or_scope_mismatch')
        if approval.get('last_modified_step') is not None:
            invalidating_steps.add(approval['last_modified_step'])
        repair_targets.add('renew_scoped_human_approval')

    all_executions_passed = True
    all_hashes_current = True
    all_timestamps_monotonic = True
    all_upstream_statuses_active = True
    all_scopes_compatible = True

    for cid in active_claim_ids:
        claim = claims[cid]
        obs_id = claim.get('observation_step_id')
        obs = observations.get(obs_id) if obs_id is not None else None
        if not obs or obs['exit_code'] != 0 or not obs['stable_during_run']:
            all_executions_passed = False
            defeated_reasons.append(f'{cid}:execution_missing_or_failed')
            if obs_id is not None:
                invalidating_steps.add(obs_id)
            repair_targets.add(cid)
            continue

        if obs['task_scope'] != decision.get('requested_scope'):
            all_scopes_compatible = False
            defeated_reasons.append(f'{cid}:scope_drift({obs["task_scope"]}!={decision.get("requested_scope")})')
            invalidating_steps.add(obs_id)
            repair_targets.add(cid)

        for fname, recorded_hash in obs['before_hashes'].items():
            current_art = artifacts.get(fname)
            if not current_art:
                all_hashes_current = False
                defeated_reasons.append(f'{cid}:missing_artifact({fname})')
                repair_targets.add(fname)
                continue
            if current_art['sha256'] != recorded_hash:
                all_hashes_current = False
                defeated_reasons.append(f'{cid}:stale_artifact_hash_drift({fname})')
                if current_art.get('last_modified_step') is not None:
                    invalidating_steps.add(current_art['last_modified_step'])
                repair_targets.add(cid)
            if current_art.get('status', 'active') != 'active':
                all_upstream_statuses_active = False
                defeated_reasons.append(f'{cid}:upstream_artifact_retracted({fname})')
                if current_art.get('last_modified_step') is not None:
                    invalidating_steps.add(current_art['last_modified_step'])
                repair_targets.add(fname)
            if current_art.get('last_modified_step', 0) > obs['step_id']:
                all_timestamps_monotonic = False
                defeated_reasons.append(f'{cid}:artifact_modified_after_test({fname})')
                invalidating_steps.add(current_art['last_modified_step'])
                repair_targets.add(cid)

        for parent_cid in claim.get('upstream_claims', []):
            parent_claim = claims.get(parent_cid)
            if not parent_claim:
                all_timestamps_monotonic = False
                defeated_reasons.append(f'{cid}:missing_parent_claim({parent_cid})')
                repair_targets.add(parent_cid)
                continue
            parent_obs = observations.get(parent_claim.get('observation_step_id'))
            if not parent_obs or parent_obs['step_id'] > obs['step_id']:
                all_timestamps_monotonic = False
                defeated_reasons.append(f'{cid}:non_monotonic_parent_step({parent_cid})')
                if parent_obs:
                    invalidating_steps.add(parent_obs['step_id'])
                repair_targets.add(cid)

    checks['transitive_executions_passed'] = all_executions_passed
    checks['transitive_artifact_hashes_current'] = all_hashes_current
    checks['transitive_timestamps_monotonic'] = all_timestamps_monotonic
    checks['transitive_sources_active'] = all_upstream_statuses_active
    checks['transitive_scopes_compatible'] = all_scopes_compatible

    required_branches = decision.get('required_independent_branches', 1)
    top_claims = decision.get('supporting_claims', [])
    branch_warrant_sets = []
    for top_cid in top_claims:
        branch_queue = [top_cid]
        branch_visited = set()
        warrants = set()
        while branch_queue:
            bc = branch_queue.pop(0)
            if bc in branch_visited or bc not in claims:
                continue
            branch_visited.add(bc)
            b_obs = observations.get(claims[bc].get('observation_step_id'))
            if b_obs:
                for imp in b_obs.get('ast_imports', []):
                    if f'{imp}.py' in artifacts:
                        warrants.add(f'module:{imp}.py')
                for arg_name in b_obs.get('arg_names', []):
                    if 'calib' in arg_name or 'shared' in arg_name or 'split' in arg_name:
                        warrants.add(f'data:{arg_name}')
            for p_cid in claims[bc].get('upstream_claims', []):
                branch_queue.append(p_cid)
        branch_warrant_sets.append(warrants)

    shared_warrants = set()
    if len(branch_warrant_sets) >= 2:
        for i in range(len(branch_warrant_sets)):
            for j in range(i + 1, len(branch_warrant_sets)):
                shared_warrants |= (branch_warrant_sets[i] & branch_warrant_sets[j])

    effective_independent_branches = len(top_claims) - (len(top_claims) - 1 if shared_warrants else 0)
    warrant_independence_ok = (len(top_claims) >= required_branches) and (not shared_warrants)
    checks['warrant_independence_vertex_cut'] = warrant_independence_ok
    if not warrant_independence_ok:
        defeated_reasons.append(
            f'correlated_warrant_collapse(shared={sorted(shared_warrants)}, '
            f'effective_branches={effective_independent_branches}<{required_branches})'
        )
        for sw in shared_warrants:
            art_key = sw.split(':', 1)[-1]
            if art_key in artifacts and artifacts[art_key].get('last_modified_step') is not None:
                invalidating_steps.add(artifacts[art_key]['last_modified_step'])
            repair_targets.add(f'decouple_shared_warrant:{art_key}')

    semantic_slice_ok = True
    semantic_flags = []
    if include_stage2_semantic_slice:
        active_files_source = {
            fname: artifacts[fname]['content']
            for fname in ancestors['active_artifact_names']
            if fname in artifacts and fname.endswith('.py')
        }
        semantic_flags = inspect_semantic_slice_ast(active_files_source)
        semantic_slice_ok = len(semantic_flags) == 0
        checks['stage2_causal_slice_semantic_integrity'] = semantic_slice_ok
        if not semantic_slice_ok:
            for flag in semantic_flags:
                defeated_reasons.append(f'stage2_semantic_hack({flag})')
                fname = flag.split(':', 1)[0]
                if fname in artifacts and artifacts[fname].get('last_modified_step') is not None:
                    invalidating_steps.add(artifacts[fname]['last_modified_step'])
                repair_targets.add(f'audit_and_replace_tampered_script:{fname}')

    permitted = all(checks.values())
    return dict(
        permit=permitted,
        verdict='accept' if permitted else 'suspend',
        checks=checks,
        defeated_reasons=defeated_reasons,
        invalidating_steps=sorted(invalidating_steps),
        causal_slice=ancestors,
        statutory_contestability_record=dict(
            claim=decision.get('statement', 'Certify safety case for deployment'),
            principal_grounds_ancestors=ancestors['active_claim_ids'],
            bound_host_artifacts=ancestors['active_artifact_names'],
            effective_independent_branches=effective_independent_branches,
            required_independent_branches=required_branches,
            shared_warrants_detected=sorted(shared_warrants),
            oversight_compression=f"{ancestors['causal_slice_steps']}/{ancestors['total_steps']} steps in causal slice ({ancestors['step_compression_ratio']*100:.1f}% pruned)",
            unmet_gates=[k for k, v in checks.items() if not v],
            minimal_repair_set=sorted(repair_targets) if not permitted else [],
            eu_ai_act_research_mapping={
                'art_12_record_keeping': 'Derives decision records from host-observed subprocess outcomes and artifact hashes; full observation retention remains separate',
                'art_13_transparency': 'Lists configured ancestor claims, bound artifact names, and unmet checks',
                'art_14_human_oversight': 'Prunes dead-branch logs for review and withholds permission on defeated warrants; human benefit is untested',
                'art_15_robustness': 'Checks observed dependency drift and shared warrants; optional Stage-2 flags selected AST tampering patterns',
                'art_55_72_lifecycle_invalidation': 'Automatically suspends downstream safety claims when upstream calibration or shared harnesses drift or retract',
                'art_86_contestability': 'Provides machine-checkable defeated_reasons and minimal_repair_set to contest or restore a decision',
            },
        ),
    )


def conventional_1hop_revalidation(dag_state: dict) -> bool:
    decision = dag_state['decision']
    claims = dag_state['claims']
    artifacts = dag_state['artifacts']
    observations = dag_state['observations']
    approval = dag_state.get('approval') or {}

    if not approval.get('active') or approval.get('task_scope') != decision.get('requested_scope'):
        return False
    top_claims = decision.get('supporting_claims', [])
    if set(approval.get('approved_claims', [])) != set(top_claims):
        return False

    for cid in top_claims:
        claim = claims.get(cid)
        if not claim:
            return False
        obs = observations.get(claim.get('observation_step_id'))
        if not obs or obs['exit_code'] != 0 or not obs['stable_during_run']:
            return False
        if obs['task_scope'] != decision.get('requested_scope'):
            return False
        for fname in claim.get('bound_artifacts', []):
            if fname not in artifacts or artifacts[fname].get('status', 'active') != 'active':
                return False
            if obs['before_hashes'].get(fname) != artifacts[fname]['sha256']:
                return False
    return True


def flat_hash_manifest_check(dag_state: dict) -> bool:
    decision = dag_state['decision']
    claims = dag_state['claims']
    artifacts = dag_state['artifacts']
    observations = dag_state['observations']
    approval = dag_state.get('approval') or {}

    if not approval.get('active'):
        return False
    for cid in decision.get('supporting_claims', []):
        obs = observations.get(claims[cid].get('observation_step_id'))
        if not obs or obs['exit_code'] != 0:
            return False
    for fname, art in artifacts.items():
        if art.get('status') == 'retracted':
            return False
        matching_obs = [
            obs for obs in observations.values()
            if obs['before_hashes'].get(fname) == art['sha256'] and obs['exit_code'] == 0
        ]
        if fname.endswith('.py') and not matching_obs and art.get('used_in_active_claims', True):
            return False
    return True


def unpruned_transcript_monitor(dag_state: dict) -> bool:
    all_steps = dag_state.get('all_trajectory_steps', [])
    if len(all_steps) <= 10:
        window_steps = all_steps
    else:
        window_steps = all_steps[:4] + all_steps[-4:]

    for s in window_steps:
        if s.get('exit_code', 0) != 0 or s.get('has_semantic_hack_in_window', False):
            return False
        if s.get('event_type') in {'revoke_approval', 'retract_artifact'}:
            return False
    return True
