package workitems

// Work-items schema for L1 (company-level) programs.
// Self-contained - no external dependencies.
//
// PURPOSE:
// L1 work-items are PLANNING ARTIFACTS for company-level coordination.
// They track work like template individualization, repo bootstrapping.
//
// NOT operational - the scheduler only runs on L0 (FCOS) work-items.
// Use this schema for validation: cue vet work-items.json work-items.cue
//
// State machine defined in: governance-kernel/governance/fcos/state-machine.yaml
// States: triage | queued | doing | review | done

#State: "triage" | "queued" | "doing" | "review" | "done"
#ParallelMode: "parallel-safe" | "exclusive"

#Task: {
	text: string
	done: bool
}

#IssueContext: {
	read_first:      [...string]
	read_if_blocked: [...string]
}

#IssueContract: {
	context:        #IssueContext
	writable_roots: [...string]
	lock_keys:      [...string]
	parallel_mode:  #ParallelMode
}

#Issue: {
	id:          string
	title:       string
	state:       #State
	repo:        [...string]
	depends_on:  [...string]
	labels:      [...string]
	tasks:       [#Task, ...#Task]
	dod:         string
	validation:  [...string]
	rollback:    string
	contract:    #IssueContract
	completed_at?: string & =~"^[0-9]{4}-[0-9]{2}-[0-9]{2}$"
	note?:       string
}

#Milestone: {
	id:     string & =~"^M[0-9]+$"
	title:  string
	issues: [...#Issue]
}

#WorkItems: {
	schema_version: 1
	updated_at:     string & =~"^[0-9]{4}-[0-9]{2}-[0-9]{2}$"
	owner:          string
	naming_contract: {
		system_name:    string
		issue_prefix:   string
		tool_namespace: string
	}

	milestones:  [...#Milestone]
	program_dod: [...string]
}
