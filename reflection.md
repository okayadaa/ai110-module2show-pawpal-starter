# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design:
Based on my UML design, the Owner following attributes is having their own unique id, first name, and last name. Along with pet's info. Therefore, owner owns pet. Owner's pet attibutes has first name, last name, and age. Owner uses Owner scheduler which following attribute has chackboxes, date, duration, and priorities. Thats where it would generate Daily Schedule and displaying Daily Plan. Owner has Owner tasks. Owner tasks includes walks, feeding, medications, appointments, and other.
  
- What classes did you include, and what responsibilities did you assign to each:
The four given classes is Owner, Pet, Tasks, and Scheduler.
For Owner class, there responsibilites is user have their own unique id and their info is contain which includes their first name, last name, and their pet. For Pet class, it's the owner pet info such as first name, last name, age, and any special needs. For Task class, it's user's keeping track of their pet's walks, feeding, medications, appointments, and other (custom). For Scheduler class, it's purpose is where it generates a plan for the user on specific task that must be completed based on it's priorities. 

**b. Design changes**

- Did your design change during implementation:
Yes, the only specific changes I made is DailyPlan and Scheduler because DailyPlan would summarize and explain the final schedule. Scheduler would have their own algorithm in order to build a plan based on the tasks.
- If yes, describe at least one change and why you made it:
One change I made is DailyPlan is to not summarize and explain. Instead to display the list of task that user inputted. And Scheduler would sort the priority and filter feasible to build a plan for the owner. 

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
