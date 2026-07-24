# AI Ethics Review — Crystal Cavern

## Topic: Authorship, transparency, and environmental cost in AI-assisted procedural design

Crystal Cavern uses generative AI as a programming and research assistant. This creates a clear ethical question: if an AI system proposes code or an algorithm, what remains the student's original design work? My position is that authorship in this project lies in the human decisions that determine the problem, constraints, evaluation criteria, parameter ranges, visual direction and final selection—not in an uncredited copy of model output.

### 1. What AI did, and what the author did

| Stage | AI-assisted contribution | Human responsibility and evidence |
|---|---|---|
| Research | Suggested search terms and candidate algorithms | Chose tunnel graph over terrain after critique; checked source papers and project fit |
| Implementation | Drafted Python/Maya API patterns | Ran code in Maya, fixed API/runtime failures, organised modules and versioned scene files |
| Visual iteration | Helped diagnose material, camera and lighting problems | Selected real cave references; rejected unsuccessful renders; set final aesthetic constraints |
| Communication | Helped outline English narration | Recorded demonstration, disclosed use, and personally explains the algorithm and trade-offs |

### 2. Transparency protocol

The deliverable includes an AI-use table, this review, prompt examples and iteration files. Each generated scene is saved separately. The presentation labels AI as an implementation assistant and never claims that a rendered image or an algorithm was manually produced when it was not. This makes the work auditable by the instructor.

### 3. Academic integrity

AI support is ethically acceptable only if the author can explain and modify the submitted work. Therefore, the presentation demonstrates a parameter change in Maya, explains the tunnel graph, and shows the L-system rule `F → F[+F][-F]`. The final submission does not treat an AI answer as evidence; the cited papers are the evidence for the algorithms.

### 4. Environmental cost

Generative AI and repeated high-resolution rendering both consume compute. This project reduces unnecessary use by validating with low-resolution Arnold look-dev renders, keeping a small reusable material set, and using deterministic seeds rather than regenerating scenes blindly. Final 1080p rendering is reserved for selected scenes. Efficiency is not only technical—it is a design ethics decision.

### 5. Conclusion

The responsible use of AI here is transparent augmentation: it accelerates implementation, while the author remains accountable for design intent, technical validation, attribution, and resource use. The boundary is crossed when a student cannot explain, test, or disclose the generated work.

## References

- UNESCO. (2023). *Guidance for Generative AI in Education and Research*.
- Prusinkiewicz, P., & Lindenmayer, A. (1990). *The Algorithmic Beauty of Plants*.
