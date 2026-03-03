from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import logging

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key')
# enable debug logging for session inspection
app.logger.setLevel(logging.DEBUG)

import json
from datetime import datetime, timedelta
import random

# custom jinja filter to format timestamps

def datetimeformat(ts):
    try:
        return datetime.fromtimestamp(float(ts)).isoformat(sep=' ')
    except Exception:
        return ts

app.jinja_env.filters['datetimeformat'] = datetimeformat

# Sample questions for each subject
QUESTIONS = {
    "physics": [
        {"q": "What is the unit of force?", "options": ["Newton", "Joule", "Meter"], "answer": "Newton"},
        {"q": "What is the acceleration due to gravity on Earth?", "options": ["9.8 m/s^2", "9.8 m/s^2", "10 m/s^2"], "answer": "9.8 m/s^2"},
        {"q": "What is the unit of force?", "options": ["Newton", "Joule", "Meter"], "answer": "Newton"},
        {"q": "Which physical quantity is measured in Joules?", "options": ["Energy", "Pressure", "Velocity"], "answer": "Energy"},
        {"q": "What is the acceleration due to gravity on Earth?", "options": ["9.8 m/s^2", "10 m/s", "9.8 kg/m^3"], "answer": "9.8 m/s^2"},
        {"q": "Which instrument is used to measure electric current?", "options": ["Ammeter", "Voltmeter", "Barometer"], "answer": "Ammeter"},
        {"q": "What is the unit of electrical resistance?", "options": ["Ohm", "Volt", "Ampere"], "answer": "Ohm"},
        {"q": "Which law states that V = IR?", "options": ["Ohm's Law", "Newton's First Law", "Boyle's Law"], "answer": "Ohm's Law"},
        {"q": "What type of lens converges light rays?", "options": ["Convex lens", "Concave lens", "Plane mirror"], "answer": "Convex lens"},
        {"q": "The rate of change of velocity is called?", "options": ["Acceleration", "Speed", "Momentum"], "answer": "Acceleration"},
        {"q": "What is the SI unit of power?", "options": ["Watt", "Joule", "Pascal"], "answer": "Watt"},
        {"q": "Which quantity is a vector?", "options": ["Force", "Mass", "Temperature"], "answer": "Force"},
        {"q": "What is the unit of pressure?", "options": ["Pascal", "Newton", "Joule"], "answer": "Pascal"},
        {"q": "Energy stored in a stretched spring is called?", "options": ["Elastic potential energy", "Kinetic energy", "Thermal energy"], "answer": "Elastic potential energy"},
        {"q": "The image formed by a plane mirror is?", "options": ["Virtual", "Real", "Inverted"], "answer": "Virtual"},
        {"q": "What is the speed of light in vacuum?", "options": ["3.0 x 10^8 m/s", "3.0 x 10^6 m/s", "3.0 x 10^5 km/s"], "answer": "3.0 x 10^8 m/s"},
        {"q": "Which gas law states that pressure is inversely proportional to volume?", "options": ["Boyle's Law", "Charles' Law", "Ohm's Law"], "answer": "Boyle's Law"},
        {"q": "What is the unit of frequency?", "options": ["Hertz", "Second", "Meter"], "answer": "Hertz"},
        {"q": "Which particle has a negative charge?", "options": ["Electron", "Proton", "Neutron"], "answer": "Electron"},
        {"q": "The work done when force and displacement are perpendicular is?", "options": ["Zero", "Maximum", "Negative"], "answer": "Zero"},
        {"q": "What is the unit of momentum?", "options": ["kg m/s", "Newton", "Joule"], "answer": "kg m/s"},
        {"q": "Which device converts mechanical energy to electrical energy?", "options": ["Generator", "Motor", "Transformer"], "answer": "Generator"},
        {"q": "The bending of light as it passes from one medium to another is called?", "options": ["Refraction", "Reflection", "Diffraction"], "answer": "Refraction"},
        {"q": "Which mirror can form a real image?", "options": ["Concave mirror", "Plane mirror", "Convex mirror"], "answer": "Concave mirror"},
        {"q": "The unit of capacitance is?", "options": ["Farad", "Henry", "Tesla"], "answer": "Farad"},
        {"q": "Heat transfer through solids occurs mainly by?", "options": ["Conduction", "Convection", "Radiation"], "answer": "Conduction"},
        {"q": "Which quantity is measured in watts per square meter?", "options": ["Intensity", "Voltage", "Charge"], "answer": "Intensity"},
        {"q": "The time taken for one complete oscillation is called?", "options": ["Period", "Frequency", "Amplitude"], "answer": "Period"},
        {"q": "What is the unit of electric charge?", "options": ["Coulomb", "Volt", "Ampere"], "answer": "Coulomb"},
        {"q": "The property of a body to resist change in motion is?", "options": ["Inertia", "Momentum", "Velocity"], "answer": "Inertia"},
        {"q": "Which law explains floating of bodies?", "options": ["Archimedes' Principle", "Ohm's Law", "Hooke's Law"], "answer": "Archimedes' Principle"},
        {"q": "The SI unit of magnetic flux is?", "options": ["Weber", "Tesla", "Henry"], "answer": "Weber"},
        {"q": "Which wave does not require a material medium?", "options": ["Electromagnetic wave", "Sound wave", "Water wave"], "answer": "Electromagnetic wave"},
        {"q": "What is the unit of density?", "options": ["kg/m^3", "g/cm", "N/m"], "answer": "kg/m^3"},
        {"q": "The splitting of white light into colours is?", "options": ["Dispersion", "Refraction", "Interference"], "answer": "Dispersion"},
        {"q": "What is the unit of work?", "options": ["Joule", "Watt", "Newton"], "answer": "Joule"},
        {"q": "Which device is used to measure atmospheric pressure?", "options": ["Barometer", "Thermometer", "Hygrometer"], "answer": "Barometer"},
        {"q": "The increase in length per unit length per degree rise in temperature is?", "options": ["Coefficient of linear expansion", "Specific heat capacity", "Thermal conductivity"], "answer": "Coefficient of linear expansion"},
        {"q": "Which quantity is measured in Tesla?", "options": ["Magnetic field strength", "Electric current", "Resistance"], "answer": "Magnetic field strength"},
        {"q": "The ability to do work is called?", "options": ["Energy", "Power", "Force"], "answer": "Energy"},
        {"q": "What type of motion has constant acceleration?", "options": ["Uniformly accelerated motion", "Circular motion", "Random motion"], "answer": "Uniformly accelerated motion"},
        {"q": "The unit of inductance is?", "options": ["Henry", "Farad", "Ohm"], "answer": "Henry"},
        {"q": "Which colour has the highest frequency?", "options": ["Violet", "Red", "Green"], "answer": "Violet"},
        {"q": "The turning effect of a force is called?", "options": ["Moment", "Pressure", "Impulse"], "answer": "Moment"},
        {"q": "The unit of impulse is?", "options": ["N s", "Joule", "Watt"], "answer": "N s"},
        {"q": "What is the SI unit of temperature?", "options": ["Kelvin", "Celsius", "Fahrenheit"], "answer": "Kelvin"},
        {"q": "Which quantity remains constant in uniform circular motion?", "options": ["Speed", "Velocity", "Acceleration"], "answer": "Speed"},
        {"q": "What is the unit of electric potential difference?", "options": ["Volt", "Coulomb", "Ohm"], "answer": "Volt"},
        {"q": "The change in momentum per unit time is?", "options": ["Force", "Impulse", "Power"], "answer": "Force"},
        {"q": "Which phenomenon explains the formation of rainbow?", "options": ["Dispersion", "Reflection", "Polarization"], "answer": "Dispersion"},
        {"q": "The resistance of a conductor depends on?", "options": ["Length", "Colour", "Shape only"], "answer": "Length"},
        {"q": "Which law states that for every action, there is an equal and opposite reaction?", "options": ["Newton's Third Law", "Newton's First Law", "Kepler's Law"], "answer": "Newton's Third Law"}


    ],
    "chemistry": [
        {"q": "What is the chemical symbol for water?", "options": ["H2O", "CO2", "O2"], "answer": "H2O"},
        {"q": "Which is an alkali metal?", "options": ["Sodium", "Oxygen", "Chlorine"], "answer": "Sodium"},
    ],
    "maths": [
        {"q": "What is 2 + 2?", "options": ["3", "4", "5"], "answer": "4"},
        {"q": "What is the area of a circle with radius r?", "options": ["πr^2", "2πr", "πd"], "answer": "πr^2"},
    ],

    "gst": [
    

        {"q": "When an adjective is placed before a noun, it is said to be in what position?", "options": ["Predicative", "Attributive", "Complementive", "Appositive"], "answer": "Attributive"},
        {"q": "The major components of a sentence are:", "options": ["Phrase and clause", "The subject and the predicate", "Verb and object", "Noun and verb"], "answer": "The subject and the predicate"},
        {"q": "A verb which always occurs with an object is a/an _______ verb.", "options": ["Intransitive", "Transitive", "Linking", "Auxiliary"], "answer": "Transitive"},
        {"q": "Which clause pattern is reflected in: 'The plane took off at noon'?", "options": ["SVO", "SVC", "SVA", "SVOA"], "answer": "SVA"},
        {"q": "Which clause pattern is reflected in: 'The tribunal conducted the hearing behind closed doors'?", "options": ["SVC", "SVO", "SVOA", "SVOC"], "answer": "SVOA"},
        {"q": "Which clause pattern is reflected in: 'Kofi became the president'?", "options": ["SVO", "SVC", "SVA", "SVOC"], "answer": "SVC"},
        {"q": "Which clause pattern is reflected in: 'The guards caught the thief'?", "options": ["SVC", "SVA", "SVO", "SV"], "answer": "SVO"},
        {"q": "Which clause pattern is reflected in: 'The priest pronounced the couple man and wife'?", "options": ["SVOC", "SVOA", "SVOO", "SVC"], "answer": "SVOC"},
        {"q": "Which clause pattern is reflected in: 'Jesus wept'?", "options": ["SVO", "SVC", "SVA", "SV"], "answer": "SV"},
        {"q": "In the sentence 'We bought John a guitar', what does 'a guitar' function as?", "options": ["Indirect object", "Subject complement", "Object complement", "Direct object"], "answer": "Direct object"},
        {"q": "The study of the arrangement of constituents within a sentence is called:", "options": ["Syntax", "Morphology", "Phonology", "Semantics"], "answer": "Syntax"},
        {"q": "Grammar is broadly classified into:", "options": ["Phonology and syntax", "Syntax and morphology", "Semantics and pragmatics", "Morphology and phonetics"], "answer": "Syntax and morphology"},
        {"q": "Grammatical hierarchy in English is structured as:", "options": ["Word, phrase, clause, sentence", "Morpheme, word, phrase, clause and sentence", "Phrase, word, clause, sentence", "Sentence, clause, phrase, word"], "answer": "Morpheme, word, phrase, clause and sentence"},
        {"q": "Which one of the following coordinating conjunctions is NOT used in compound sentences?", "options": ["And", "But", "Or", "So that"], "answer": "So that"},
        {"q": "Which subordinating conjunction CANNOT introduce an adverb clause?", "options": ["Although", "When", "Nevertheless", "If"], "answer": "Nevertheless"},
        {"q": "A ---------- is a group of words that contain a subject and a predicate.", "options": ["Phrase", "Clause", "Sentence", "Modifier"], "answer": "Clause"},
        {"q": "Identify the interrogative sentence.", "options": ["Take the bus home.", "She went home.", "Do walk quickly.", "Where are you going?"], "answer": "Where are you going?"},
        {"q": "Declarative sentences end with a:", "options": ["Comma", "Colon", "Question mark", "Period"], "answer": "Period"},
        {"q": "Interrogative sentences ___________.", "options": ["Give commands", "Express emotion", "Make statements", "Ask questions"], "answer": "Ask questions"},
        {"q": "A complex sentence has:", "options": ["Two independent clauses", "No clause", "One clause", "One independent clause and one or more dependent clauses"], "answer": "One independent clause and one or more dependent clauses"},
        {"q": "There are how many basic clause patterns in the English simple sentence?", "options": ["5", "6", "7", "8"], "answer": "7"},
        {"q": "Which one of the following is a simple sentence?", "options": ["The boy killed the snake and ran away.", "Although he came, he left early.", "The boy killed the snake.", "When he arrived, we left."], "answer": "The boy killed the snake."},
        {"q": "Prepositions begin phrases that end with:", "options": ["Verb", "Adjective", "Adverb", "Either a noun or pronoun"], "answer": "Either a noun or pronoun"},
        {"q": "The smallest unit of a word is known as:", "options": ["Syllable", "Morpheme", "Phoneme", "Lexeme"], "answer": "Morpheme"},
        {"q": "Free morphemes are sub-categorized into:", "options": ["Lexical and functional", "Prefix and suffix", "Derivational and inflectional", "Root and stem"], "answer": "Lexical and functional"},
        {"q": "The word 'unhappily' contains:", "options": ["Root only", "Prefix and root", "Prefix, root, suffix", "Suffix only"], "answer": "Prefix, root, suffix"},
        {"q": "Prefixes and suffixes are generally known as:", "options": ["Roots", "Stems", "Bases", "Affixes"], "answer": "Affixes"},
        {"q": "As a prefix, ANTI- means:", "options": ["Before", "Against", "After", "Without"], "answer": "Against"},
        {"q": "The prominence of one syllable over others in a word is a function of:", "options": ["Stress", "Tone", "Pitch", "Length"], "answer": "Stress"},
        {"q": "English stress is:", "options": ["Fixed", "Predictable", "Final", "Free"], "answer": "Free"},
        {"q": "Yes/No questions are naturally asked using the _______ tune.", "options": ["Rising", "Falling", "Level", "Broken"], "answer": "Rising"},
        {"q": "The ______ tune is used in declarative sentences.", "options": ["Rising", "Level", "Broken", "Falling"], "answer": "Falling"},
        {"q": "Another name for the soft palate is the:", "options": ["Alveolar ridge", "Velum", "Larynx", "Pharynx"], "answer": "Velum"},
        {"q": "The label 'bilabial glide' refers to:", "options": ["/j/", "/l/", "/w/", "/h/"], "answer": "/w/"},
        {"q": "Voicing occurs as a result of the ________ of the vocal folds.", "options": ["Closure", "Opening", "Friction", "Vibration"], "answer": "Vibration"},
        {"q": "A syllable with a CV structure is said to be:", "options": ["Open", "Closed", "Complex", "Heavy"], "answer": "Open"},
        {"q": "High vowels are also described as _______ vowels.", "options": ["Front", "Close", "Back", "Rounded"], "answer": "Close"},
        {"q": "A maximum of _______ consonants are permissible at the beginning of an English syllable.", "options": ["2", "3", "4", "5"], "answer": "3"},
        {"q": "The only compulsory element in a syllable is the:", "options": ["Onset", "Coda", "Vowel", "Consonant"], "answer": "Vowel"},
        {"q": "Two models of spelling popular in English are:", "options": ["Formal and informal", "Old and modern", "British and American", "Classical and modern"], "answer": "British and American"},
        {"q": "Symbols used in phonetic transcription are adapted from:", "options": ["ASCII", "Latin alphabet", "Unicode", "IPA"], "answer": "IPA"},
        {"q": "Features which apply to units higher than segments are known as:", "options": ["Segments", "Phonemes", "Suprasegmentals", "Allophones"], "answer": "Suprasegmentals"},
        {"q": "The first step in reading a passage is to _______ it.", "options": ["Scan", "Read deeply", "Preview", "Summarize"], "answer": "Preview"},
        {"q": "In _______ we read to get the overall idea.", "options": ["Skimming", "Scanning", "Studying", "Surveying"], "answer": "Skimming"},
        {"q": "In scanning, the reader seeks to:", "options": ["Main idea", "Inference", "Theme", "Specific information"], "answer": "Specific information"},
        {"q": "The main purpose of reading is to _______ a written material.", "options": ["Memorize", "Criticize", "Comprehend", "Translate"], "answer": "Comprehend"},
        {"q": "A comprehension passage is best understood when it is read:", "options": ["Once", "Quickly", "Silently", "More than once"], "answer": "More than once"},
    
        {"q": "Reading for the purpose of gathering information that will translate to knowledge is also known as:", "options": ["Study reading", "Skimming", "Scanning", "Previewing"], "answer": "Study reading"},
        {"q": "Study reading does NOT:", "options": ["Enhance reading speed", "Improve comprehension", "Improve retention", "Aid exam performance"], "answer": "Enhance reading speed"},
        {"q": "The mnemonic _______ serves as a guide to productive study reading.", "options": ["SQ3R", "LEARNER", "PQRST", "OK4R"], "answer": "LEARNER"},
        {"q": "Which of the following is NOT a standard reading technique?", "options": ["3RQS", "SQ3R", "PQRST", "3S3R"], "answer": "3RQS"},
        {"q": "SQ3R refers to:", "options": ["Survey, Question, Read", "Survey, Query, Read", "Survey, Question, 3R", "Scan, Question, Read"], "answer": "Survey, Question, 3R"},
        {"q": "3R stands for:", "options": ["Read, Repeat, Review", "Review, Recall, Recite", "Read, Recall, Review", "Read, Recite, Respond"], "answer": "Read, Recall, Review"},
        {"q": "In reviewing an item you have read, one of the following is not necessary:", "options": ["Headings", "References", "Annotated notes", "Highlighted sections"], "answer": "References"},
        {"q": "-------------------- is a receptive skill.", "options": ["Writing", "Reading", "Speaking", "Debating"], "answer": "Reading"},
        {"q": "The movement of the eyes in reading can be described as:", "options": ["Saccadic", "Linear", "Circular", "Vertical"], "answer": "Saccadic"},
        {"q": "When our eyes make a backward movement during reading, it is known as:", "options": ["Fixation", "Scanning", "Skipping", "Regression"], "answer": "Regression"},
        {"q": "------------------- is the process of translating written/printed symbols into words and sentences.", "options": ["Writing", "Reading", "Encoding", "Speaking"], "answer": "Reading"},
        {"q": "Clear thinking, accurate data, reliable authority and clear conclusion are applicable to ________ essay.", "options": ["Narrative", "Descriptive", "Argumentative", "Analytical"], "answer": "Analytical"},
        {"q": "A _______ essay gives a detailed and often dispassionate account of people, incidents, scenes and situations.", "options": ["Argumentative", "Descriptive", "Narrative", "Expository"], "answer": "Descriptive"},
        {"q": "The _______ essay emphasizes character and setting.", "options": ["Descriptive", "Analytical", "Narrative", "Persuasive"], "answer": "Narrative"},
        {"q": "Biographies and autobiographies can be classified under _______ essay.", "options": ["Analytical", "Descriptive", "Expository", "Narrative"], "answer": "Narrative"},
        {"q": "A/an _______ paragraph explains how or why something happens.", "options": ["Explanation", "Sequence", "Narrative", "Argument"], "answer": "Explanation"},
        {"q": "The thesis statement is to an essay what the _______ is to a paragraph.", "options": ["Topic sentence", "Conclusion", "Transition", "Hook"], "answer": "Topic sentence"},
        {"q": "Unity in a paragraph suggests:", "options": ["Length", "Complexity", "Variety", "Singularity of focus"], "answer": "Singularity of focus"},
        {"q": "The element which makes a paragraph easily understandable to the reader is:", "options": ["Unity", "Length", "Coherence", "Style"], "answer": "Coherence"},
        {"q": "One of the following is NOT an element of a paragraph:", "options": ["Unity", "Coherence", "Duration", "Topic sentence"], "answer": "Duration"},
        {"q": "One of the following is NOT true about writing a summary:", "options": ["It is concise", "It paraphrases ideas", "It captures main points", "Quotations from the text are included"], "answer": "Quotations from the text are included"},
        {"q": "In essay writing, the acronym COEM means:", "options": ["Content, Organisation, Evaluation, Method", "Clarity, Order, Evidence, Mechanics", "Content, Organisation, Expression, Mechanics", "Concept, Opinion, Evidence, Meaning"], "answer": "Content, Organisation, Expression, Mechanics"},
        {"q": "............. is referred to as the meat of the essay.", "options": ["Organisation", "Expression", "Content", "Mechanics"], "answer": "Content"},
        {"q": "The ............ is the major point which an essay seeks to prove.", "options": ["Thesis", "Topic", "Title", "Theme"], "answer": "Thesis"},
        {"q": "Regular/normal conversations usually attract _______ listening.", "options": ["Formal", "Critical", "Informal", "Academic"], "answer": "Informal"},
        {"q": "During lectures, we engage in _______ listening.", "options": ["Informal", "Formal", "Casual", "Passive"], "answer": "Formal"},
        {"q": "Listening can be categorised into _______ and _______.", "options": ["Active and passive", "Formal and informal", "Critical and analytical", "Primary and secondary"], "answer": "Formal and informal"},
        {"q": "Note-taking complements:", "options": ["Reading", "Writing", "Speaking", "Listening"], "answer": "Listening"},
        {"q": "Speech defect is a _______ condition hampering effective listening.", "options": ["Psychological", "Emotional", "Physiological", "Environmental"], "answer": "Physiological"},
        {"q": "Noise is a _______ condition.", "options": ["Psychological", "Spiritual", "Physical", "Emotional"], "answer": "Physical"},
        {"q": "A group of words that behave like a single word with a single meaning is known as:", "options": ["Idiom", "Phrase", "Clause", "Collocation"], "answer": "Collocation"},
        {"q": "............. is the plural of datum.", "options": ["Datas", "Datums", "Datae", "Data"], "answer": "Data"},
        {"q": "When the meaning of a word is considered in isolation, it is known as ______ meaning.", "options": ["Connotative", "Contextual", "Denotative", "Figurative"], "answer": "Denotative"},
        {"q": "The suitable reference source for background and current information on any field is:", "options": ["Dictionary", "Encyclopaedia", "Atlas", "Manual"], "answer": "Encyclopaedia"},
        {"q": "The acronym 'OPAC' means:", "options": ["Online Public Access Catalogue", "Open Public Academic Centre", "Official Public Archive Catalogue", "Online Private Access Collection"], "answer": "Online Public Access Catalogue"},
        {"q": "Combination of letters and figures indicating the classes of a book is known as:", "options": ["Index", "Catalogue", "Call mark", "Accession number"], "answer": "Call mark"},
        {"q": "An _______ summarizes the accurate content and presentation of a document.", "options": ["Index", "Review", "Abstract", "Preface"], "answer": "Abstract"},
        {"q": "............. collections are not expected to be read from cover to cover.", "options": ["Serial", "Journal", "Textbook", "Reference"], "answer": "Reference"},
        {"q": "Publications conveying recent original research are known as:", "options": ["Magazines", "Newspapers", "Journals", "Manuals"], "answer": "Journals"},
        {"q": "Copyrighted works are protected by:", "options": ["Law", "Publisher", "Author", "Library"], "answer": "Law"},
        {"q": "............. is the act of using copyrighted work without permission.", "options": ["Citation", "Referencing", "Fair use", "Plagiarism"], "answer": "Plagiarism"},
        {"q": "Referencing is composed of two parts, namely:", "options": ["Citation and bibliography", "In-text referencing and reference list", "Footnote and endnote", "Abstract and index"], "answer": "In-text referencing and reference list"},
        {"q": "A quote is used in research write-up to:", "options": ["Lengthen the essay", "Summarize", "Criticize", "Support an argument"], "answer": "Support an argument"},
        {"q": "One of the attributes of information is:", "options": ["Length", "Relevance", "Size", "Color"], "answer": "Relevance"},
        {"q": "Information can be evaluated using the following criteria EXCEPT:", "options": ["Authority", "Size", "Currency", "Accuracy"], "answer": "Size"},
        {"q": "Ability to locate, retrieve and evaluate information is known as:", "options": ["Information storage", "Information literacy", "Data processing", "Information management"], "answer": "Information literacy"},
        {"q": "The ability to recognize when information is needed is called:", "options": ["Data awareness", "Library skills", "Information literacy", "Search competence"], "answer": "Information literacy"},
        {"q": "Effective use of library resources requires:", "options": ["Search strategies", "Guess work", "Memorization", "Browsing only"], "answer": "Search strategies"},
        {"q": "One of the major benefits of using library databases is:", "options": ["Free internet access", "Social networking", "Entertainment materials", "They are subscribed to by the library to support students' assignments and research"], "answer": "They are subscribed to by the library to support students' assignments and research"},
        {"q": "When results are too broad, the way out is to:", "options": ["Stop searching", "Use fewer words", "Change your search strategy", "Ignore results"], "answer": "Change your search strategy"},
        {"q": "When there are too few sources, one can:", "options": ["Combine synonymous terms with the OR Boolean operator", "Delete keywords", "Stop searching", "Use NOT operator"], "answer": "Combine synonymous terms with the OR Boolean operator"},
        {"q": "Boolean operators are:", "options": ["IF, THEN, ELSE", "AND, OR, NOT", "IN, ON, AT", "FOR, WITH, BY"], "answer": "AND, OR, NOT"},
        {"q": "The Boolean operator OR is used to:", "options": ["Narrow search", "Exclude terms", "Connect synonyms", "End search"], "answer": "Connect synonyms"},
        {"q": "'AND' is used as a Boolean operator when you want to _______ your results.", "options": ["Broaden", "Expand", "Define/Narrow", "Duplicate"], "answer": "Define/Narrow"},
        {"q": "The 'NOT' operator is used to:", "options": ["Broaden search", "Exclude & narrow search", "Connect synonyms", "Sort results"], "answer": "Exclude & narrow search"},
        {"q": "The following are search techniques EXCEPT:", "options": ["Filtering", "Boolean operators", "Wild card", "Truncation"], "answer": "Filtering"},
        {"q": "Employing the use of various search engines in an electronic search is referred to as:", "options": ["Single search", "Manual search", "Database search", "Meta search"], "answer": "Meta search"},
        {"q": "When a user deploys a variety of search tools simultaneously, it is called:", "options": ["Advanced search", "Meta search", "Subject search", "Manual search"], "answer": "Meta search"},
        {"q": "The asterisk sign (*) in a search is known as:", "options": ["Hash tag", "Truncation mark", "Colon", "Wild card"], "answer": "Wild card"},
        {"q": "When keywords are embedded in quotes, the type of search is:", "options": ["Subject search", "Title search", "Keyword search", "Phrase search"], "answer": "Phrase search"},
        {"q": "............. is done to reduce items retrieved in advanced search.", "options": ["Sorting", "Browsing", "Scanning", "Filtering"], "answer": "Filtering"},
        {"q": "All of these are advantages of using advanced search EXCEPT:", "options": ["Filtering options", "Precision searching", "Ability to retrieve huge amount of information", "Multiple search fields"], "answer": "Ability to retrieve huge amount of information"},
        {"q": "Advanced search allows you to limit your searches by:", "options": ["Author only", "Title only", "Publisher only", "Year of publication"], "answer": "Year of publication"},
        {"q": "Subject Searching allows one to:", "options": ["Search by author", "Search by title", "Search randomly", "Browse for items by subject"], "answer": "Browse for items by subject"},
        {"q": "Students can search the manual library catalogue using:", "options": ["Author/title & subject", "Language only", "Publisher only", "ISBN only"], "answer": "Author/title & subject"},
        {"q": "Ranking of articles retrieved from databases is by:", "options": ["Color and size", "Alphabet only", "Length only", "Date and relevance"], "answer": "Date and relevance"},
        {"q": "Reference materials include the following EXCEPT:", "options": ["Dictionaries", "Journals", "Encyclopaedias", "Handbooks"], "answer": "Journals"},
        {"q": "Notable reference collection includes all of these EXCEPT:", "options": ["Encyclopaedias", "Dictionaries", "Books", "Almanacs"], "answer": "Books"},
        {"q": "A Closed Access System refers to:", "options": ["Open shelves", "Online access", "Restricted access", "Free browsing"], "answer": "Restricted access"},
        {"q": "The research and bibliographic section of the library houses:", "options": ["Children books", "PhD thesis and newspapers", "Fiction only", "Magazines only"], "answer": "PhD thesis and newspapers"},
        {"q": "Biographical sources provide individual information such as:", "options": ["Date of birth only", "Career achievements only", "Place of birth only", "All of the above"], "answer": "All of the above"},
        {"q": "Biographical sources are categorized into:", "options": ["Old and new", "Printed and electronic", "Local and foreign", "Universal and current"], "answer": "Universal and current"},
        {"q": "A thesaurus is a:", "options": ["Story book", "Atlas", "Specialised dictionary", "Magazine"], "answer": "Specialised dictionary"},
        {"q": "Yearbooks are also known as:", "options": ["Diaries", "Annual", "Biographies", "Abstracts"], "answer": "Annual"},
        {"q": "An ............. is a summary of a publication or article.", "options": ["Index", "Abstract", "Catalogue", "Glossary"], "answer": "Abstract"},
        {"q": "A secondary source is one that _______ a primary source.", "options": ["Ignores", "Analyzes & explains", "Replaces", "Copies"], "answer": "Analyzes & explains"},
        {"q": "Secondary source is more reliable than primary source:", "options": ["True", "Sometimes", "Often", "False"], "answer": "False"},
        {"q": "Libraries perform all of these functions EXCEPT:", "options": ["Acquisition", "Book selling", "Organization", "Preservation"], "answer": "Book selling"},
        {"q": "Types of libraries include all of these EXCEPT:", "options": ["Court", "Academic", "Public", "National"], "answer": "Court"},
        {"q": "Letter T is assigned to books on _______ in the Library of Congress Classification Scheme.", "options": ["Medicine", "Science", "Technology", "Arts"], "answer": "Technology"},
        {"q": "Which letters cannot be found in the Library of Congress Classification Scheme?", "options": ["Letter O", "Letter A", "Letter H", "Letter Q"], "answer": "Letter O"},
        {"q": "Mixed notation refers to the use of letters of the alphabet as well as:", "options": ["Roman numerals", "Symbols", "Arabic numerals", "Greek letters"], "answer": "Arabic numerals"},
        {"q": "Arrangement of materials on the shelves is done using:", "options": ["Classification scheme", "Alphabet only", "Color code", "Size order"], "answer": "Classification scheme"},
        {"q": "Arrangement in the library catalogue is in _______ order.", "options": ["Numerical", "Chronological", "Random", "Alphabetical"], "answer": "Alphabetical"},
        {"q": "Electronic journals, electronic images, library software, CD-ROMs are:", "options": ["Print resources", "Non-print resources", "Reference books", "Manual resources"], "answer": "Non-print resources"},
        {"q": "Radio, tape-recorder, gramophone, and audio cassette player are examples of:", "options": ["Audio materials", "Visual materials", "Print materials", "Digital books"], "answer": "Audio materials"},
        {"q": "The person who provides reference services is called:", "options": ["Archivist", "Reference Librarian", "Publisher", "Editor"], "answer": "Reference Librarian"},
        {"q": "Information can be in the form of:", "options": ["Texts only", "Numbers only", "Graphs only", "All of the above"], "answer": "All of the above"},
        {"q": "Any information retrieved from the Internet can be considered accurate:", "options": ["True", "Always", "False", "Often"], "answer": "False"},
        {"q": "The main kinds of electronic materials in most libraries are:", "options": ["E-books and e-periodicals", "Printed books", "Magazines only", "Newspapers only"], "answer": "E-books and e-periodicals"},
        {"q": "One of the following is not a terminal punctuation mark:", "options": ["Full stop", "Question mark", "Exclamation mark", "Comma"], "answer": "Comma"},
        {"q": "Interjections are usually punctuated with a:", "options": ["Comma", "Semicolon", "Colon", "Exclamation mark"], "answer": "Exclamation mark"},
        {"q": "An ellipsis is a series of:", "options": ["Two periods", "Four periods", "Three periods", "Five periods"], "answer": "Three periods"},
        {"q": "The word 'boyish' has _____ morphemes.", "options": ["2", "1", "3", "4"], "answer": "2"}



        
        ],

}

@app.route('/')
def index():
    app.logger.debug('index session contents: %r', dict(session))
    expires = None
    if 'expires_at' in session:
        try:
            expires = datetime.fromtimestamp(session['expires_at']).isoformat()
        except Exception:
            expires = session.get('expires_at')
    return render_template('index.html', subjects=QUESTIONS.keys(), expires_display=expires)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # clear anything leftover from a previous session (old expiry strings etc.)
    if request.method == 'GET':
        session.clear()
        # also clear the client cookie by sending an empty one
        from flask import make_response
        resp = make_response(render_template('login.html'))
        resp.set_cookie('session', '', expires=0)
        return resp
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            flash('Please enter a name to log in.')
            return redirect(url_for('login'))
        session['username'] = name
        now = datetime.utcnow()
        session['start_time'] = now.isoformat()
        # store expiration as a timestamp (seconds since epoch) to avoid
        # timezone parsing issues in JavaScript
        session['expires_at'] = (now + timedelta(minutes=30)).timestamp()
        # debug output
        app.logger.debug('login session contents: %r', dict(session))
        flash(f'Logged in as {name}. You have 30 minutes and up to 60 questions per subject.')
        return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.')
    return redirect(url_for('index'))

@app.route('/quiz/<subject>', methods=['GET', 'POST'])
def quiz(subject):
    if subject not in QUESTIONS:
        return redirect(url_for('index'))
    # require login
    if 'username' not in session:
        flash('Please log in before taking a quiz.')
        return redirect(url_for('login'))

    # check expiry (expires stored as timestamp) and normalize if necessary
    expires = session.get('expires_at')
    if isinstance(expires, str):
        try:
            expires = float(expires)
            session['expires_at'] = expires
        except ValueError:
            expires = None
    if expires:
        try:
            now_ts = datetime.utcnow().timestamp()
            if now_ts > expires:
                session.clear()
                return render_template('timeout.html')
        except Exception as e:
            app.logger.error('expiry check error: %s', e)
            session.clear()
            return render_template('timeout.html')

    # prepare questions for this quiz request; statelessly sample indices and send them in the form
    all_q = QUESTIONS[subject]
    if request.method == 'GET':
        count = min(60, len(all_q))
        indices = random.sample(range(len(all_q)), count) if len(all_q) > count else list(range(len(all_q)))
        questions = [all_q[i] for i in indices]
    else:  # POST
        # indices are posted back as JSON string
        import json as _json
        indices_str = request.form.get('indices', '[]')
        try:
            indices = _json.loads(indices_str)
        except Exception:
            indices = []
        questions = [all_q[i] for i in indices] if indices else []

    if request.method == 'POST':
        name = session.get('username', '')
        score = 0
        answers = []
        # build a details list we can send back to the template so the student
        # can review which items they got right or wrong
        details = []
        for i, q in enumerate(questions):
            selected = request.form.get(f"q{i}")
            answers.append(selected)
            correct = (selected == q['answer'])
            if correct:
                score += 1
            details.append({
                'question': q['q'],
                'options': q.get('options', []),
                'selected': selected,
                'answer': q['answer'],
                'correct': correct
            })
        total = len(questions)
        # compute percentage grade (scale to 100)
        percentage = round((score / total) * 100, 2) if total else 0

        # record result; keep indices so we can reconstruct later if needed
        result = {
            'name': name,
            'subject': subject,
            'score': score,
            'total': total,
            'percentage': percentage,
            'indices': indices,
            'answers': answers,
            'details': details,
            'timestamp': datetime.utcnow().isoformat()
        }
        save_result(result)
        return render_template('result.html', subject=subject, score=score, total=total,
                               percentage=percentage, name=name, details=details)

    # pass numeric expiry and the chosen indices to the template for JS handling
    return render_template('quiz.html', subject=subject, questions=questions, expires_at=session.get('expires_at'), indices=indices)



def results_file_path():
    return os.path.join(os.path.dirname(__file__), 'results.json')


def read_results():
    path = results_file_path()
    if not os.path.exists(path):
        return []
    with open(path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_result(entry):
    path = results_file_path()
    data = read_results()
    data.append(entry)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


@app.route('/grades')
def grades():
    results = read_results()
    return render_template('grades.html', results=results)

@app.route('/history')
def history():
    if 'username' not in session:
        flash('Please log in to view your history.')
        return redirect(url_for('login'))
    username = session.get('username')
    all_results = read_results()
    user_results = [r for r in all_results if r.get('name') == username]
    return render_template('history.html', results=user_results, username=username)

if __name__ == '__main__':
    app.run(debug=True)
