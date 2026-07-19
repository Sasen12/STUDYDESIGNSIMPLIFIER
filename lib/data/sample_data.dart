import '../models/study_item.dart';

final List<StudyItem> sampleItems = [
  // ── Software Development ──────────────────────────────────────────
  StudyItem(
    id: 'sd_1',
    subject: 'Software Development',
    title: 'Problem-Solving Methodology',
    category: 'Key Knowledge',
    officialText:
        'The problem-solving methodology is a structured approach consisting of eight stages: analyse, design, develop, test, evaluate, implement, document, and maintain. These stages form the Software Development Life Cycle (SDLC).',
    plainLanguageText:
        'The steps you follow when building software: figure out the problem (analyse), plan the solution (design), write the code (develop), check for bugs (test), see if it works (evaluate), release it (implement), write it down (document), and keep updating it (maintain).',
    unit: 'Unit 3',
    areaOfStudy: 'Area of Study 1',
    outcome: 'Outcome 1',
  ),
  StudyItem(
    id: 'sd_2',
    subject: 'Software Development',
    title: 'Agile vs Waterfall',
    category: 'Key Knowledge',
    officialText:
        'Agile is an iterative approach to software development that emphasises flexibility, customer collaboration, and rapid delivery of working software. Waterfall is a linear, sequential approach where each phase must be completed before the next begins.',
    plainLanguageText:
        'Agile is flexible — you build a little, show it to the client, get feedback, and repeat. Waterfall is rigid — you do every stage in order without going back. Agile is best for projects that might change; Waterfall is better when the requirements are clear from the start.',
    unit: 'Unit 3',
    areaOfStudy: 'Area of Study 1',
    outcome: 'Outcome 1',
  ),
  StudyItem(
    id: 'sd_3',
    subject: 'Software Development',
    title: 'Compare',
    category: 'Command Term',
    officialText:
        'Provide an account of the similarities and differences between two or more items, referring to both (or all) of them throughout.',
    plainLanguageText:
        'Say how things are alike AND different. Don\'t just describe one — you need to talk about both and make direct comparisons.',
    unit: 'Unit 3',
    areaOfStudy: 'Area of Study 1',
    outcome: 'Outcome 1',
  ),
  StudyItem(
    id: 'sd_4',
    subject: 'Software Development',
    title: 'Justify',
    category: 'Command Term',
    officialText:
        'Provide reasons, evidence or arguments that support a conclusion. Explain why a decision, selection or approach is appropriate.',
    plainLanguageText:
        'Don\'t just say "I used Agile." You need to explain WHY you used Agile for this specific project — give reasons that prove it was the right choice.',
    unit: 'Unit 3',
    areaOfStudy: 'Area of Study 1',
    outcome: 'Outcome 1',
  ),
  StudyItem(
    id: 'sd_5',
    subject: 'Software Development',
    title: 'Design Thinking',
    category: 'Key Knowledge',
    officialText:
        'Design thinking is a human-centred, iterative problem-solving process that involves five stages: empathise, define, ideate, prototype, and test.',
    plainLanguageText:
        'Design thinking puts the user first. You start by understanding their needs (empathise), then define the problem clearly, brainstorm solutions (ideate), build a simple version (prototype), and try it out (test).',
    unit: 'Unit 3',
    areaOfStudy: 'Area of Study 2',
    outcome: 'Outcome 2',
  ),
  StudyItem(
    id: 'sd_6',
    subject: 'Software Development',
    title: 'Validate solution requirements',
    category: 'Key Skill',
    officialText:
        'Validate solution requirements against the functional and non-functional requirements, ensuring alignment with client needs and project scope.',
    plainLanguageText:
        'Check that what you\'re building actually matches what the client asked for. Go through the list of requirements one by one and make sure your solution does each thing it\'s supposed to do.',
    unit: 'Unit 3',
    areaOfStudy: 'Area of Study 2',
    outcome: 'Outcome 2',
  ),
  StudyItem(
    id: 'sd_7',
    subject: 'Software Development',
    title: 'Evaluate',
    category: 'Command Term',
    officialText:
        'Assess the worth, quality or significance of something using a set of criteria. Include a judgement about its merit or effectiveness.',
    plainLanguageText:
        'You need to judge something — is it good or bad? Give it a score based on criteria and explain WHY you gave that rating. A conclusion is required.',
    unit: 'Unit 3',
    areaOfStudy: 'Area of Study 1',
    outcome: 'Outcome 1',
  ),
  StudyItem(
    id: 'sd_8',
    subject: 'Software Development',
    title: 'Cybersecurity — OWASP Top 10',
    category: 'Key Knowledge',
    officialText:
        'The OWASP Top 10 is a standard awareness document listing the ten most critical security risks to web applications, including injection, broken authentication, sensitive data exposure, and cross-site scripting.',
    plainLanguageText:
        'A list of the 10 most common ways web apps get hacked. Things like SQL injection (someone types \' OR 1=1 — into a form), stolen passwords, exposed credit card data, and malicious scripts. You should know these to build secure apps.',
    unit: 'Unit 4',
    areaOfStudy: 'Area of Study 1',
    outcome: 'Outcome 1',
  ),

  // ── Data Analytics ────────────────────────────────────────────────
  StudyItem(
    id: 'da_1',
    subject: 'Data Analytics',
    title: 'Data Types — Structured vs Unstructured',
    category: 'Key Knowledge',
    officialText:
        'Structured data is highly organised and easily searchable in relational databases, typically stored in rows and columns. Unstructured data lacks a predefined format, including text, images, audio, and video files.',
    plainLanguageText:
        'Structured data is neat and tidy — like an Excel spreadsheet with columns and rows. Unstructured data is messy — like emails, photos, videos, or social media posts. Each needs different tools to analyse.',
    unit: 'Unit 3',
    areaOfStudy: 'Area of Study 1',
    outcome: 'Outcome 1',
  ),
  StudyItem(
    id: 'da_2',
    subject: 'Data Analytics',
    title: 'CRISP-DM Framework',
    category: 'Key Knowledge',
    officialText:
        'CRISP-DM (Cross-Industry Standard Process for Data Mining) is a six-phase framework: Business Understanding, Data Understanding, Data Preparation, Modelling, Evaluation, and Deployment.',
    plainLanguageText:
        'The standard way to run a data science project:\n1. Understand the business problem\n2. Find and explore the data\n3. Clean and prepare the data\n4. Build a model\n5. Check if it works\n6. Put it into production',
    unit: 'Unit 3',
    areaOfStudy: 'Area of Study 2',
    outcome: 'Outcome 2',
  ),
  StudyItem(
    id: 'da_3',
    subject: 'Data Analytics',
    title: 'Analyse',
    category: 'Command Term',
    officialText:
        'Examine the components or structure of something, identifying patterns, relationships, and implications.',
    plainLanguageText:
        'Break something down into its parts and explain how they fit together. Look for trends, connections, and what it all means.',
    unit: 'Unit 3',
    areaOfStudy: 'Area of Study 1',
    outcome: 'Outcome 1',
  ),
  StudyItem(
    id: 'da_4',
    subject: 'Data Analytics',
    title: 'Data Wrangling / Cleaning',
    category: 'Key Knowledge',
    officialText:
        'Data wrangling is the process of cleaning, transforming, and enriching raw data into a format suitable for analysis. Common tasks include handling missing values, removing duplicates, and standardising formats.',
    plainLanguageText:
        'Real-world data is messy. Data wrangling means cleaning it up: filling in missing values, removing duplicate rows, making sure dates are in the same format, and fixing typos — so your analysis isn\'t garbage.',
    unit: 'Unit 3',
    areaOfStudy: 'Area of Study 2',
    outcome: 'Outcome 2',
  ),
  StudyItem(
    id: 'da_5',
    subject: 'Data Analytics',
    title: 'Describe',
    category: 'Command Term',
    officialText:
        'Provide a detailed account of the characteristics, features or qualities of something.',
    plainLanguageText:
        'Just describe what\'s there — what it looks like, what it does, what features it has. No need to explain why or judge it.',
    unit: 'Unit 3',
    areaOfStudy: 'Area of Study 1',
    outcome: 'Outcome 1',
  ),

  // ── Business Management ───────────────────────────────────────────
  StudyItem(
    id: 'bm_1',
    subject: 'Business Management',
    title: 'Management Styles — Autocratic',
    category: 'Key Knowledge',
    officialText:
        'Autocratic management is a style where the manager makes all decisions unilaterally with little or no input from employees. Communication is typically one-way, from manager to employees.',
    plainLanguageText:
        'The boss makes all the decisions alone. Employees just do what they\'re told. Fast but can demotivate the team. Best in a crisis where quick decisions are needed.',
    unit: 'Unit 3',
    areaOfStudy: 'Area of Study 2',
    outcome: 'Outcome 2',
  ),
  StudyItem(
    id: 'bm_2',
    subject: 'Business Management',
    title: 'Corporate Social Responsibility (CSR)',
    category: 'Key Knowledge',
    officialText:
        'CSR refers to a business\'s commitment to operating in an economically, socially, and environmentally sustainable manner while balancing the interests of stakeholders.',
    plainLanguageText:
        'CSR means a company doesn\'t just care about profit — it also tries to do good: reduce waste, treat workers fairly, give back to the community, and be environmentally responsible.',
    unit: 'Unit 4',
    areaOfStudy: 'Area of Study 1',
    outcome: 'Outcome 1',
  ),
  StudyItem(
    id: 'bm_3',
    subject: 'Business Management',
    title: 'Distinguish',
    category: 'Command Term',
    officialText:
        'Show how two or more items are different. Identify the characteristics that set them apart.',
    plainLanguageText:
        'Focus only on the differences. Don\'t waste time on similarities — just say what makes them different from each other.',
    unit: 'Unit 3',
    areaOfStudy: 'Area of Study 1',
    outcome: 'Outcome 1',
  ),
  StudyItem(
    id: 'bm_4',
    subject: 'Business Management',
    title: 'SWOT Analysis',
    category: 'Key Knowledge',
    officialText:
        'SWOT analysis is a strategic planning tool used to evaluate the Strengths, Weaknesses, Opportunities, and Threats involved in a business or project.',
    plainLanguageText:
        'A SWOT analysis is like a business health check. Look internally at what you\'re good at (Strengths) and bad at (Weaknesses), and externally at opportunities you can grab and threats that might harm you.',
    unit: 'Unit 3',
    areaOfStudy: 'Area of Study 2',
    outcome: 'Outcome 2',
  ),

  // ── General Mathematics ───────────────────────────────────────────
  StudyItem(
    id: 'gm_1',
    subject: 'General Mathematics',
    title: 'Recurrence Relations',
    category: 'Key Knowledge',
    officialText:
        'A recurrence relation is an equation that recursively defines a sequence where the next term is a function of the previous term(s). The general form is t_{n+1} = r × t_n + d.',
    plainLanguageText:
        'A way to get the next number in a sequence from the current one. Like "add 3 each time" or "multiply by 1.05 each year." Great for modelling things that grow or shrink step by step.',
    unit: 'Unit 3',
    areaOfStudy: 'Area of Study 1',
    outcome: 'Outcome 1',
  ),
  StudyItem(
    id: 'gm_2',
    subject: 'General Mathematics',
    title: 'Calculate',
    category: 'Command Term',
    officialText:
        'Determine a numerical value using a mathematical process, showing working.',
    plainLanguageText:
        'Do the maths and show your steps. Use your CAS calculator but write down what you put in so the examiner can see your method.',
    unit: 'Unit 3',
    areaOfStudy: 'Area of Study 1',
    outcome: 'Outcome 1',
  ),
  StudyItem(
    id: 'gm_3',
    subject: 'General Mathematics',
    title: 'Linear Regression (Least Squares)',
    category: 'Key Knowledge',
    officialText:
        'Least squares regression is a statistical method used to find the line of best fit for a set of data by minimising the sum of squared residuals between observed and predicted values.',
    plainLanguageText:
        'Drawing the straight line that best matches your scatter plot points. It minimises the total distance from each point to the line. Your CAS does all the hard work.',
    unit: 'Unit 4',
    areaOfStudy: 'Area of Study 2',
    outcome: 'Outcome 2',
  ),

  // ── English ───────────────────────────────────────────────────────
  StudyItem(
    id: 'en_1',
    subject: 'English',
    title: 'Analyse Argument and Language',
    category: 'Key Skill',
    officialText:
        'Analyse how authors use language, persuasive devices, and structural choices to position an audience and achieve a purpose in a text.',
    plainLanguageText:
        'When you read an article or speech, ask: what is the author trying to make me think/feel/do? How are they doing it — emotive language, rhetorical questions, statistics? Break it down.',
    unit: 'Unit 3',
    areaOfStudy: 'Area of Study 2',
    outcome: 'Outcome 2',
  ),
  StudyItem(
    id: 'en_2',
    subject: 'English',
    title: 'Metalanguage Glossary',
    category: 'Key Knowledge',
    officialText:
        'Metalanguage is the technical language used to describe and analyse how language works, including tone, mood, imagery, symbolism, syntax, diction, and figurative devices.',
    plainLanguageText:
        'The fancy terms for talking about writing: tone (attitude), mood (feeling), imagery (word pictures), symbolism (what things represent), syntax (sentence structure), diction (word choice), and figurative language (metaphors, similes).',
    unit: 'Unit 3',
    areaOfStudy: 'Area of Study 1',
    outcome: 'Outcome 1',
  ),
  StudyItem(
    id: 'en_3',
    subject: 'English',
    title: 'Explain',
    category: 'Command Term',
    officialText:
        'Provide a detailed account of how or why something occurs, clarifying the reasons, causes, or mechanisms involved.',
    plainLanguageText:
        'Don\'t just say what happened — say HOW and WHY. Walk through the cause and effect chain.',
    unit: 'Unit 3',
    areaOfStudy: 'Area of Study 1',
    outcome: 'Outcome 1',
  ),

  // ── Physics ───────────────────────────────────────────────────────
  StudyItem(
    id: 'ph_1',
    subject: 'Physics',
    title: 'Newton\'s Laws of Motion',
    category: 'Key Knowledge',
    officialText:
        'Newton\'s First Law (Inertia): an object remains at rest or in uniform motion unless acted on by a net external force. Second Law: F = ma. Third Law: every action has an equal and opposite reaction.',
    plainLanguageText:
        'Three simple rules: 1) Things keep doing what they\'re doing unless you push them. 2) Force equals mass times acceleration — heavy things need more force. 3) Push a wall, it pushes back equally.',
    unit: 'Unit 3',
    areaOfStudy: 'Area of Study 1',
    outcome: 'Outcome 1',
  ),
  StudyItem(
    id: 'ph_2',
    subject: 'Physics',
    title: 'Conservation of Energy',
    category: 'Key Knowledge',
    officialText:
        'The law of conservation of energy states that energy cannot be created or destroyed, only transformed from one form to another. Total energy in an isolated system remains constant.',
    plainLanguageText:
        'Energy doesn\'t disappear — it just changes form. The ball at the top has potential energy (stored). When it falls, that becomes kinetic (movement) energy. Nothing is lost, it just changes.',
    unit: 'Unit 3',
    areaOfStudy: 'Area of Study 1',
    outcome: 'Outcome 1',
  ),
  StudyItem(
    id: 'ph_3',
    subject: 'Physics',
    title: 'Identify',
    category: 'Command Term',
    officialText:
        'Recognise and name a characteristic, factor, or feature. No explanation or elaboration is required beyond identification.',
    plainLanguageText:
        'Just name it. Point at the thing and say its name. That\'s it — don\'t explain it, don\'t describe it.',
    unit: 'Unit 3',
    areaOfStudy: 'Area of Study 1',
    outcome: 'Outcome 1',
  ),
  StudyItem(
    id: 'ph_4',
    subject: 'Physics',
    title: 'Hooke\'s Law',
    category: 'Key Knowledge',
    officialText:
        'Hooke\'s Law states that the force needed to extend or compress a spring by a displacement is proportional to that displacement: F = −kx, where k is the spring constant.',
    plainLanguageText:
        'The more you stretch a spring, the harder it pulls back. Double the stretch = double the force. Negative sign means it pulls in the opposite direction to how you\'re pulling.',
    unit: 'Unit 3',
    areaOfStudy: 'Area of Study 2',
    outcome: 'Outcome 2',
  ),

  // ── Mathematical Methods ──────────────────────────────────────────
  StudyItem(
    id: 'mm_1',
    subject: 'Mathematical Methods',
    title: 'Differentiation — Power Rule',
    category: 'Key Knowledge',
    officialText:
        'The derivative of x^n with respect to x is n × x^(n−1). This is known as the power rule and applies for all real exponents n.',
    plainLanguageText:
        'To differentiate x^n (find the gradient function): bring the power down in front, then subtract 1 from the power. Example: x³ → 3x².',
    unit: 'Unit 3',
    areaOfStudy: 'Area of Study 1',
    outcome: 'Outcome 1',
  ),
  StudyItem(
    id: 'mm_2',
    subject: 'Mathematical Methods',
    title: 'Sketch',
    category: 'Command Term',
    officialText:
        'Draw a graph, indicating key features such as intercepts, asymptotes, turning points, and endpoints. Labelling is essential.',
    plainLanguageText:
        'Draw the curve and label the important bits: where it crosses the axes (intercepts), the highest/lowest points (turning points), and any dashed lines it gets close to but never touches (asymptotes).',
    unit: 'Unit 3',
    areaOfStudy: 'Area of Study 1',
    outcome: 'Outcome 1',
  ),
  StudyItem(
    id: 'mm_3',
    subject: 'Mathematical Methods',
    title: 'Integration — Definite Integrals',
    category: 'Key Knowledge',
    officialText:
        'A definite integral calculates the signed area under a curve between two limits a and b, denoted as ∫_a^b f(x) dx. The result is a number.',
    plainLanguageText:
        'The area under a graph between two points. If the area is above the x-axis, it\'s positive; below, it\'s negative. Your CAS can do the calculation — you just need to set it up correctly.',
    unit: 'Unit 3',
    areaOfStudy: 'Area of Study 2',
    outcome: 'Outcome 2',
  ),
];
