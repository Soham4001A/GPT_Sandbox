@startuml
start

:Initialize OpenAI client with API key;
:Define helper functions;

if (Start Problem Solver?) then (Yes)
    :Initialize problem description;
    :Set maximum steps and restarts;
    while (Restart allowed?) is (Yes)
        :Start new reasoning chain;
        :Reset steps and feedback logs;

        while (Steps < max_steps?) is (Yes)
            :Generate step using generate_step();
            if (Step generation error or NO_MORE_STEPS?) then (Exit loop)
                break
            else
                :Validate step with holistic_feedback_gate();
                if (Feedback suggests flaws?) then (Yes)
                    :Generate corrected step;
                    :Replace current step;
                else (No)
                    :Accept current step;
                endif
                :Add step to reasoning chain;
            endif
        endwhile

        :Run global consistency check;
        if (Global check suggests restart?) then (Yes)
            :Add identified assumptions;
        else (No)
            if (Final Answer Synthesized?) then (Yes)
                :Store Final Answer;
                break
            else (No)
                :Select most logical chain;
            endif
        endif
    endwhile

    :Output Final Answer;
else (No)
    :Exit Program;
endif

stop
@enduml
