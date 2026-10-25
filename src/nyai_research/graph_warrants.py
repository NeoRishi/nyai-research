"""Check the provenance available in a retrieval trace, never infer claim truth.

Graph links establish retrieval lineage. Entailment, applicability and currentness
remain unknown without additional evidence. Flags are review cues, not judgments.
"""


def audit_retrieval(passages, expansion, requested_citations):
    checks = []

    def add(rule, status, reason):
        checks.append(dict(rule_id=rule, status=status, reason=reason))

    if not passages:
        add('retrieval', 'failed', 'No candidate passages returned')
    else:
        add('retrieval', 'passed', f'{len(passages)} candidate passages returned')
    ids = [p.get('id') for p in passages]
    complete = all(isinstance(x, str) and x for x in ids)
    add('chunk_identity', 'passed' if complete and len(set(ids)) == len(ids) else 'failed',
        'Chunk IDs must be present and unique within this trace')
    locators = all(p.get('slug') and p.get('heading') is not None and p.get('text', '').strip() for p in passages)
    add('passage_locator', 'passed' if passages and locators else 'failed',
        'Passages must include note identity, heading and nonempty text')
    available = {f'P{i}' for i in range(1, len(passages) + 1)}
    missing = sorted(set(requested_citations) - available)
    add('citation_resolution', 'failed' if missing else 'passed',
        'Unknown citation labels: ' + ', '.join(missing) if missing else 'Requested labels resolve to retrieved passages')
    notes = {p.get('slug') for p in passages}
    expanded = {e.get('slug'): e for e in expansion}
    uncovered = notes - set(expanded)
    if not passages:
        add('source_lineage', 'unknown', 'No retrieved passage lineage to inspect')
    elif uncovered:
        add('source_lineage', 'unknown', 'Source expansion was not supplied for every selected note')
    elif any(not expanded[slug].get('sources') for slug in notes):
        add('source_lineage', 'unknown', 'Some selected notes have no CITES source entries in the supplied expansion')
    else:
        add('source_lineage', 'passed', 'Selected notes provide CITES source entries; source authenticity is not established')
    add('entailment', 'unknown', 'No independent claim-to-passage entailment review has been supplied')
    add('applicability', 'unknown', 'Retrieval relevance does not establish population, task or claim applicability')
    add('currentness', 'unknown', 'No authoritative current-source/version attestation has been supplied')
    invalid = any(c['status'] == 'failed' for c in checks)
    return dict(
        trace_status='invalid' if invalid else 'inspectable',
        validated_answer_permitted=False,
        verdict='suspend',
        checks=checks,
        decision_record=dict(
            claim='Retrieved passages are sufficient to validate an answer',
            claim_origin='constructed retrieval-sufficiency probe, not an AI-generated answer',
            warrant='Passage locators and graph source lineage can support source inspection',
            application='The trace has structural defects' if invalid else 'Inspect retrieved candidates; semantic warrants remain unknown',
            conclusion='Suspend a validated-answer claim; retrieval alone is insufficient',
            change_my_mind='Review source authenticity, currentness, entailment, scope and contrary evidence for the actual claim'))
