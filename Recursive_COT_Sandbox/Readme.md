+---------------------------------------------+
| Problem Description                         |
| (e.g., Ice cubes in a frying pan)           |
+---------------------------------------------+
              | Initialize Steps & Feedback Log
              v
+---------------------------------------------+
| Iteration Begins (Step 1)                   |
| Generate Initial Step                       |
| - Query GPT with problem description only   |
+---------------------------------------------+
              |
              v
+-----------------------+  Feedback: "No"
| Feedback Gate         |<---------------------+
| - Validate Step       |                      |
| - If "Yes": Accept    |                      |
| - If "No": Provide    |                      |
|   corrections         |                      |
+-----------------------+                      |
              |                                |
              v                                |
+-----------------------------------------+    |
| Correct Step (if "No")                  |    |
| - Refine previous steps based on        |    |
|   feedback corrections                  |    |
| - Query GPT for corrected step          |    |
+-----------------------------------------+    |
              |                                |
              v                                |
+----------------------------------------------+
| Append Valid Step to Reasoning Steps         |
| - Add corrected/accepted step                |
| - Prepare for next iteration                 |
+----------------------------------------------+
              |                                |
              v                                |
+-----------------------+                      |
| Iteration Stop Check  |                      |
| - Max steps reached?  |                      |
| - Conclusion ("Done")?|                      |
+-----------------------+                      |
              |                                |
              v                                |
+----------------------------------------------+
| Global Consistency Check                     |
| - Review full reasoning process              |
| - Validate holistic solution                 |
+----------------------------------------------+
              |
              v
+----------------------------------------------+
| Save Reasoning Steps and Final Solution      |
| - Write results to file                      |
+----------------------------------------------+