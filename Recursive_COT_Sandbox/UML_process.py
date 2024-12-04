@startuml
start
:User provides Problem Description;
:Initialize reasoning chain and feedback log;

repeat
:Generate Step using `generate_step`;
:Validate step with `holistic_feedback_gate`;
if (Feedback "Yes"?) then (Yes)
  :Accept step;
  :Append step to reasoning chain;
else (No)
  :Refine step using feedback;
  :Regenerate step with corrections;
endif
if (Max steps reached or Problem Solved?) then (Yes)
  :Pass reasoning chain to `global_consistency_check`;
  stop
else (No)
  :Continue to next step;
endif
repeat while (max steps not reached);

:Global Consistency Check evaluates all chains;
if (Flawed or Inconsistent Reasoning?) then (Yes)
  :Identify incorrect assumptions;
  :Restart process with new focus (new reasoning chain);
else (No)
  :Synthesize final answer or choose most logical chain;
endif

:Return final solution to user;
stop
@enduml
