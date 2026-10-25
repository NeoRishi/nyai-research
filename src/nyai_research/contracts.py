"""Small executable warrant contract for structured agent-action records.

This does not infer truth from prose. Inputs are assumed to come from trusted runtime
observations; tests expose what happens when that assumption fails. Fail closed when
required facts are absent. There is no universal evidence-type weight.
"""
CHECKS=(
    ('authority','Explicit action permission',lambda s:s['action'] in s['granted_actions']),
    ('consent','Current data-use consent',lambda s:s['consent'] is True),
    ('tenant','Same authorised tenant',lambda s:s['tenant']==s['authorised_tenant']),
    ('version','Evidence is current version',lambda s:s['evidence_version']==s['current_version']),
    ('integrity','Observed content hash matches expected',lambda s:s['observed_hash']==s['expected_hash']),
    ('status','Evidence remains active',lambda s:s['source_status']=='active'),
    ('scope','Evidence covers the requested task',lambda s:s['task'] in s['source_tasks']),
    ('epistemics','Evidence is an empirical execution test',lambda s:s['source_kind']=='execution_test'),
    ('contradiction','No unresolved contrary evidence',lambda s:s['unresolved_conflicts']==0),
    ('trace','Claimed checks were actually executed',lambda s:set(s['claimed_checks'])<=set(s['executed_checks'])),
    ('budget','Action fits the granted resource limit',lambda s:0<=s['requested_units']<=s['max_units']),
    ('tests','Required validation succeeded',lambda s:s['test_result']=='passed'),
)

FIELDS={
    'authority':{'action':str,'granted_actions':list},'consent':{'consent':bool},
    'tenant':{'tenant':str,'authorised_tenant':str},
    'version':{'evidence_version':int,'current_version':int},
    'integrity':{'observed_hash':str,'expected_hash':str},'status':{'source_status':str},
    'scope':{'task':str,'source_tasks':list},'epistemics':{'source_kind':str},
    'contradiction':{'unresolved_conflicts':int},
    'trace':{'claimed_checks':list,'executed_checks':list},
    'budget':{'requested_units':int,'max_units':int},'tests':{'test_result':str},
}


def adjudicate(state):
    checks=[]
    for rule_id,description,predicate in CHECKS:
        try:
            for key,kind in FIELDS[rule_id].items():
                if type(state[key]) is not kind:raise TypeError('Invalid runtime fact type')
                if kind is list and any(type(v) is not str for v in state[key]):raise TypeError('Invalid list member')
            result=bool(predicate(state))
            status='passed' if result else 'failed'
        except (KeyError,TypeError,ValueError):
            status='unknown'
        checks.append(dict(rule_id=rule_id,description=description,status=status))
    defeated=[c['rule_id'] for c in checks if c['status']!='passed']
    permitted=not defeated
    return dict(execute=permitted,verdict='accept' if permitted else 'suspend',checks=checks,
        decision_record=dict(
            claim=f"Execute requested action {state.get('action','UNKNOWN')}",
            warrant='Versioned contract over runtime observations; no semantic entailment claim',
            application='All mandatory checks passed' if permitted else 'Unmet or unknown gates: '+', '.join(defeated),
            conclusion='Execution permitted' if permitted else 'Execution withheld',
            change_my_mind='Re-evaluate after corrected runtime facts satisfy every mandatory gate'))
