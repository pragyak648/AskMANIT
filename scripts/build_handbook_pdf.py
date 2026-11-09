"""
scripts/build_handbook_pdf.py — Generates the 22-page MANIT Bhopal Student Information Handbook PDF.
"""

from pathlib import Path
import fitz

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PDF = PROJECT_ROOT / "data" / "raw" / "manit_student_handbook_2026.pdf"

PAGES = [
    # Page 1
    """MANIT Bhopal
Student Information Handbook

Maulana Azad National Institute of Technology, Bhopal: institute, programmes, admissions, MCA, campus life, placements, contacts and a website link directory.

Unofficial research compilation prepared on 1 November 2026 from public sources. Not an official MANIT publication. Verify important details on https://www.manit.ac.in.

Contents
1. About this handbook
2. MANIT at a glance
3. History and timeline
4. Campus and infrastructure
5. Academic departments
6. Programmes offered
7. Admissions guide
8. MCA at MANIT Bhopal
9. Fees and scholarships
10. Academic system, examinations and results
11. Library and learning resources
12. Hostels, food and campus services
13. Student life: fests, societies and sports
14. Training and placement
15. Rankings and accreditation
16. Research, centres and Ph.D.
17. Administration and contact directory
18. How to reach MANIT
19. Notable alumni
20. Website navigation and URL directory
21. Frequently asked questions
22. Glossary of acronyms
23. Known data conflicts and verification checklist
""",

    # Page 2
    """1. About this handbook

This handbook is an unofficial, research-based compilation of publicly available information about the Maulana Azad National Institute of Technology (MANIT), Bhopal. It was prepared on 1 November 2026 as the knowledge base for a retrieval-augmented question-answering chatbot ("Chat with MANIT"). It is not published by MANIT and must not be treated as an official document.

How reliable is each fact?
Facts are tagged with where they came from. Where sources disagree, the disagreement is stated openly instead of picking a number silently. Section 23 lists all known conflicts.

Wikipedia: The English Wikipedia article on MANIT. Generally reliable for history and campus description; some figures are dated.
Govt. portal: The Government of India science and technology portal listing for NITs. Reliable for address and phone numbers.
Aggregator: Education directory websites such as Shiksha, Careers360, CollegeDekho, Collegedunia and PaGaLGuY. Useful but frequently outdated or inconsistent, especially for fees, seats and placement figures.
News: Newspaper reports such as Free Press Journal. Reliable for events at the time of the report.
General knowledge: Widely known facts about national bodies and exams (JoSAA, CCMT, NIMCET and so on). Verify against the current notification.

Rules for the chatbot
• Answer only from this handbook. If the answer is not here, say so and point to the official website https://www.manit.ac.in.
• Always mention the source tag when giving numbers (fees, seats, placement figures, ranks).
• If the handbook shows conflicting figures, present the range and recommend checking the official notice.
• For link requests, use the URL directory in Section 20. If the entry says no trustworthy URL was found, give the main website and the navigation hint instead of guessing a link.

2. MANIT at a glance

Full name: Maulana Azad National Institute of Technology, Bhopal
Common names: MANIT, NIT Bhopal, NIT-B
Former names: Maulana Azad College of Technology (MACT); Regional Engineering College (REC), Bhopal
Motto: Education is our soul wealth (Source: Wikipedia)
Established: 4 September 1960 (Source: Wikipedia)
Named after: Maulana Abul Kalam Azad, independent India's first Minister of Education
Status: Public technical university and Institution of National Importance under the NIT Act (2007). Granted deemed university status in 2002 (Source: Wikipedia)
Funding and governance: Fully funded by the Ministry of Education, Government of India. Governed by the NIT Council (Source: Wikipedia)
Location: Bhopal, Madhya Pradesh, India
""",

    # Page 3
    """Postal address: Link Road Number 3, Near Kali Mata Mandir, Bhopal, Madhya Pradesh 462003 (Source: Govt. portal)
Campus size: About 650 acres (about 2.6 square km), one of the largest NIT campuses (Source: Wikipedia)
Language of instruction: English
Official website: https://www.manit.ac.in
Student strength (approx.): About 5,014 students: 4,017 undergraduate, 917 postgraduate and 80 doctoral. About 308 faculty. The Wikipedia infobox does not give a reference year, so treat these as approximate.
Annual festivals: Technosearch (technical), Maffick (cultural), Tooryanaad (Hindi literary and cultural)
Programmes: B.Tech, B.Arch, B.Plan, M.Tech, M.Plan, MBA, MCA, M.Sc and Ph.D.

3. History and timeline

MANIT began in 1960 as Maulana Azad College of Technology (MACT), one of the first eight Regional Engineering Colleges set up during India's Second Five-Year Plan (1956-1960) to supply trained engineers for rapid industrialisation. Each REC was a joint venture between the central government and the state government. MACT belonged to the Western Region group, together with the institutes now known as VNIT Nagpur and SVNIT Surat. (Source: Wikipedia)

The college first operated from the premises of the Swami Vivekananda Polytechnic in Bhopal, with an intake of 120 students and seven faculty members. Mr. S. R. Beedkar, Principal of the polytechnic, was appointed planning officer. In 1964 the institute shifted to its own building, which is the present campus.

Key dates
1960: Maulana Azad College of Technology (MACT) starts functioning (4 September 1960).
1961: Prime Minister Pandit Jawaharlal Nehru lays the foundation stone of the institute building on 23 April 1961.
1962: J. N. Moudgill becomes the first principal. Five-year degree programmes in Civil, Mechanical and Electrical Engineering begin.
1963: Five-year Bachelor of Architecture programme begins.
1964: Institute moves to its own campus.
1972: Electronics and Communication Engineering starts.
1986: Computer Science and Engineering starts.
1988: Three-year Master of Computer Applications (MCA) programme starts.
2001: Information Technology programme starts (merged into Computer Science and Engineering in 2013).
2002: All RECs become NITs. MACT is renamed Maulana Azad National Institute of Technology and gets deemed university status.
2003: World Bank-assisted Technical Education Quality Improvement Programme (TEQIP) begins, driving academic and infrastructure growth.
2005: Department of Computer Applications separates from the Department of Mathematics (Source: Careers360, aggregator).
2006: MBA programme begins.
2007: NIT Act passed. MANIT is declared an Institute of National Importance.
""",

    # Page 4
    """Year Event
2013: Admission switches from AIEEE to JEE Main for undergraduate programmes.
(All rows are from Wikipedia unless a different source is named.)

4. Campus and infrastructure

MANIT is spread over roughly 650 acres in Bhopal. The campus is divided into four sectors and contains administrative and academic buildings, workshops, a library and community centres, residential accommodation for students and staff, and everyday amenities. (Source: Wikipedia)

Academic and administrative facilities
• Academic blocks, workshops and laboratories for all departments.
• Central Library and a Digital Library (see Section 11).
• Computer Centre. An aggregator also reports a Central Computing Facility, a Central Research Facility and a Data Center, along with campus-wide internet connectivity (Source: Careers360).
• Sarvepalli Radhakrishnan Auditorium with a seating capacity of 1,000 persons.
• Student Activity Centre (SAC), mentioned in a student campus account (Source: GeeksforGeeks campus experience).
• Dispensary and medical care unit on campus.

Daily-life facilities
• An official branch of the State Bank of India with an ATM on the main campus.
• Post office, shopping complex and a school for children of staff.
• Food outlets reported on campus: Institute Cafeteria, Amul parlour, Nescafe huts, Teology, Neelam fast food corner and a fast food court.
• Children's park, officers' club, VIP Guest House and Faculty Guest House.
• Staff housing: 369 staff quarters (25,116 square metres built-up), faculty and officer quarters, bachelor flats and dormitories.

Sports and recreation
• Football ground, track and field ground, cricket ground, basketball courts and volleyball court.
• Gymnastics hall.
• Indoor sports complex with table tennis, chess and carrom rooms, badminton courts and a meditation hall.
• An artificial lake called Lotus Lake with the MANIT Boat Club.

Recent construction: a tender published on 29 May 2026 covers installation of sensor doors and partition work on the ground floor of the Central Library, MANIT Bhopal (tender value Rs. 24,99,472, bid end date 19 June 2026, corrigendum on 18 June 2026). This indicates ongoing library renovation. (Source: public tender listing)
""",

    # Page 5
    """5. Academic departments

The number of departments is reported differently by different sources (11 departments plus 4 specialised schools, 14 departments, or 17). The departments and centres below are the ones named across the sources reviewed. Department page links are in Section 20.

Architecture and Planning: Architecture and Planning (B.Arch, B.Plan, M.Plan in Urban Planning and Housing)
Engineering: Biological Science and Engineering; Chemical Engineering; Civil Engineering; Computer Science and Engineering; Electrical Engineering; Electronics and Communication Engineering; Mechanical Engineering; Materials Science and Metallurgical Engineering
Science: Physics (including Nanotechnology); Chemistry; Mathematics, Bioinformatics and Computer Applications (MBC)
Humanities: Humanities (English, communication and social sciences)
Management: Department of Management Studies (DMS) which runs the MBA
Centres: Centre for Artificial Intelligence; Centre for Excellence in Water Management; Product Design and Smart Manufacturing; Cable Technology (Source: aggregators)

Where the MCA programme sits
In the institute's PG programme list (session 2022-23) the MCA is offered by the department named Mathematics, Bioinformatics and Computer Applications (MBC). Historically the Department of Computer Applications separated from the Department of Mathematics in 2005. Research areas reported for the Computer Applications group are cloud computing, computer networking, information retrieval and data mining. (Sources: PG programme list, Careers360)

6. Programmes offered

Undergraduate Programmes:
• B.Tech (Civil, Mechanical, Electrical, Electronics and Communication, Computer Science, Chemical, Materials and Metallurgical, and others) — 4 years — Entry: JEE Main, then JoSAA / CSAB counselling
• B.Arch (Architecture) — 5 years — Entry: JEE Main Paper 2 (Architecture)
• B.Plan (Planning) — 4 years — Entry: JEE Main Paper 2

Postgraduate Programmes:
• M.Tech in about 24 to 27 specialisations (about 21 seats each in the 2021 listing) — 2 years — Entry: GATE, then CCMT counselling
• M.Plan (Urban Planning, Housing) — 2 years — Entry: GATE / CCMT route
• MCA (Master of Computer Applications) — 3 years (6 semesters) — Entry: NIMCET
• MBA (Department of Management Studies) — 2 years — Entry: CAT / MAT / CMAT, then GD and interview
• M.Sc (for example Mathematics, in older listings) — 2 years — Entry: Institute process

Doctoral:
• Ph.D. in engineering, science, management and architecture — Variable duration — Entry: Institute entrance and interview, twice a year
""",

    # Page 6
    """Course work and examinations are conducted in English. Admission to undergraduate programmes is highly competitive; Wikipedia states that only about the top 5 percent of applicants are able to secure admission. B.Tech seats were reported as about 800 in one aggregator listing; check the current JoSAA seat matrix for the exact intake.

7. Admissions guide

Undergraduate (B.Tech, B.Arch, B.Plan)
• Appear in JEE Main conducted by the National Testing Agency (https://jeemain.nta.ac.in). B.Arch and B.Plan use JEE Main Paper 2.
• Register and fill choices on the JoSAA counselling portal (https://josaa.nic.in). Later vacant-seat rounds are run through CSAB (https://csab.nic.in).
• Eligibility: Class 12 with Physics, Chemistry and Mathematics as compulsory subjects. One aggregator quotes at least 75 percent aggregate marks; the official requirement is set each year in the JoSAA information bulletin and should be confirmed there.
• Documents commonly asked for: JEE Main score card, Class 10 and 12 marksheets, category certificate where applicable, Aadhaar card and photographs. OBC-NCL and EWS certificates must be in the prescribed format and recent.
• Until 2013 the entrance route was AIEEE; JEE Main replaced it.

NRI and foreign students
Admission for NRIs and foreign nationals is conducted through DASA (Direct Admission of Students Abroad), which asks for qualifying SAT Subject Test scores in Physics, Chemistry and Mathematics. Scholarship-based admission is also offered through the Indian Council for Cultural Relations (ICCR). Students from countries such as Afghanistan, Bangladesh, Bhutan, Nepal, Sri Lanka, Kuwait, Saudi Arabia, Qatar, Oman and the UAE join every year. (Source: Wikipedia)

M.Tech and M.Plan
Admission is through GATE followed by CCMT counselling (https://ccmt.admissions.nic.in). Reported M.Tech admission categories include Sponsored, Self-financed and Part-time (Source: Shiksha, aggregator).

MCA
Admission is through the NIT MCA Common Entrance Test (NIMCET). Details are in Section 8.

MBA
Admission uses CAT, MAT or CMAT scores. Shortlisted candidates appear for a Group Discussion and Personal Interview round held by the institute. One aggregator notes that MBA applications may also be made directly on the institute's admission portal.

Ph.D.
Ph.D. admissions are held twice a year (Autumn and Spring sessions). For the Autumn 2026 session, the notification was published on the official website with an application deadline of 20 May 2026 and result declaration around 15 June 2026; about 200 seats were reported across departments. Applications are made online through the registration link in the Quick Links section of the website. (Source: Physics Wallah, aggregator)

The 2026-27 admission cycle has already concluded for B.Tech (JoSAA 2026 rounds finished), M.Tech (CCMT 2026) and MCA (NIMCET 2026 counselling). Prospective students should watch for the 2027 notifications.
""",

    # Page 7
    """8. MCA at MANIT Bhopal

The Master of Computer Applications is one of MANIT's oldest postgraduate programmes. It started in 1988 as a three-year programme (Source: Wikipedia). One aggregator describes the department as one of the pioneering departments of the institute and among the top five offering MCA in the country; that is a promotional claim and not an official ranking (Source: Careers360).

Duration: 3 years, 6 semesters. One aggregator lists 2 years, which conflicts with the institute's own PG programme list and Wikipedia; the 3-year structure is the one to trust.
Department: Mathematics, Bioinformatics and Computer Applications (MBC), as per the PG programme list for 2022-23.
Entrance exam: NIMCET (NIT MCA Common Entrance Test), conducted by one of the participating NITs on rotation. NIMCET 2024 was an online test held in June 2024 (Source: aggregators).
Seats: 115 in the 2022-23 PG programme list and the NIMCET Wikipedia table. Older listings show 60. Check the current NIMCET seat matrix.
Eligibility: A bachelor's degree such as BCA, B.Sc. (Computer Science) or an equivalent with Mathematics studied at Class 12 or graduation level, subject to minimum aggregate marks with relaxation for reserved categories. Confirm the exact marks in the current NIMCET brochure.
Exam coverage: NIMCET tests mathematics, analytical ability and logical reasoning, computer awareness and general English (General knowledge, verify in the brochure).
Reported cutoffs: For the General category, aggregators reported a closing rank of about 347 in 2023 and a similar band (347 to 350) for a 2025 special round. Cutoffs change every year and by category.
Fees (indicative): About Rs. 1.0 lakh in the first year: Rs. 56,500 for semester 1 and Rs. 43,500 for later semesters, including Rs. 35,000 tuition per semester (Source: Collegedunia, aggregator). Hostel and mess charges are extra.
Research strengths: Cloud computing, computer networking, information retrieval and data mining (Source: Careers360).
Contact for admissions: admission@manit.ac.in (listed in the NIMCET information brochure).

Why this matters for ML, AI and Data Science careers
The institute has set up a Centre for Artificial Intelligence and a Centre of Excellence for Artificial Intelligence, and offers an M.Tech in Artificial Intelligence (reported fee about Rs. 1,87,000 per year, admission through GATE and CCMT). MCA students can use the central computing facilities and take part in the technical societies and fests described in Section 13 to build project experience.

The official MCA scheme and syllabus (semester-wise course list) was not available when this handbook was compiled, so course names are deliberately not listed here. For the best chatbot answers, add the department's official MCA curriculum PDF to the knowledge base.
""",

    # Page 8
    """9. Fees and scholarships

Fees at NITs are revised periodically and differ by programme, category and year. The figures below come from aggregator websites that frequently disagree. Treat them as indicative and always confirm on the official fee notice.

Reported fee figures:
• B.Tech: About Rs. 1,44,250 per year (listing for Civil Engineering); another listing shows a wider range of Rs. 2.35 lakh to Rs. 5 lakh (Sources: CollegeDekho, TargetAdmission)
• B.Arch: About Rs. 3.56 lakh total as listed (Source: TargetAdmission)
• M.Tech: About Rs. 1.87 lakh per year (M.Tech in Artificial Intelligence); range Rs. 1.69 to 2.3 lakh (Sources: CollegeDekho, TargetAdmission)
• MBA: Rs. 2.77 lakh total in one listing; Rs. 1.89 lakh for two years in another (Sources: TargetAdmission, CampusOption)
• MCA: About Rs. 1.0 lakh in year 1 (Rs. 56,500 + Rs. 43,500); range Rs. 1.4 to 2.88 lakh total in another listing (Sources: Collegedunia, TargetAdmission)
• Ph.D.: Rs. 57,800 to Rs. 70,000 (Source: TargetAdmission)

Scholarships
Government and institute scholarships are reported to be available for SC, ST, OBC and EWS candidates (Source: aggregator). Students should check the scholarship notices on the official website and the National Scholarship Portal each year. For NRI and foreign students, ICCR scholarships are available (Source: Wikipedia).

10. Academic system, examinations and results

MANIT follows a semester system. Examinations are reported as Mid Semester and End (Annual) Semester examinations, and results are published on the official website roughly 30 to 35 days after the exams are completed. Programme results for UG, PG and Ph.D. are available as downloadable PDFs. (Source: PaGaLGuY, aggregator)

How to check results
• Go to the official website https://www.manit.ac.in.
• Open the Academic section from the main menu.
• Open the Examination section and select the result you need.
• Download the result PDF. (Navigation path as reported by an aggregator; the menu may have been renamed.)

Academic rules: what could and could not be verified
MANIT's own academic ordinance (attendance requirement, grading scale, backlog and re-examination rules, minimum CGPA for the degree) could not be retrieved while compiling this handbook. Rules found for other institutes must not be assumed to apply at MANIT. NITs in general use a credit-based semester system with SGPA and CGPA on a 10-point scale, but the exact thresholds are set by MANIT's Senate.

To answer rule questions correctly, add the following official documents to the knowledge base: the MANIT academic ordinance for PG / MCA, the MCA scheme and syllabus booklet, and the academic calendar. These can be requested from the Academic section (Assistant Registrar, Academics) at academic@manit.ac.in.
""",

    # Page 9
    """Typical questions the Academic section handles
• Semester registration, course enrolment and fee payment.
• Mark sheets, transcripts and degree certificates.
• Re-evaluation, supplementary examination and backlog queries.
• Bonafide certificates and no-dues certificates.

11. Library and learning resources

The MANIT Library is a functional unit of the Institute and works under the overall administrative control of the Director and the Professor In-charge (Library). (Source: AglaSem, aggregator)

Central Library: Holds a large collection of books, CDs, videos, periodicals, newspapers and bound back volumes, with subscriptions to national and international journals (Source: Careers360).
Digital Library: A Digital Library is part of the campus facilities (Source: Wikipedia and student accounts).
Library staff roles: A Librarian and Section Head, a Deputy Librarian and an Assistant Librarian are listed in a public contact directory.
Current work: A tender dated 29 May 2026 covers sensor doors and partition work on the ground floor of the Central Library.
Library website: No MANIT library web address could be verified. To find it, open https://www.manit.ac.in and look for the Library entry in the menus or use the site search for the word Library. Do not guess a library URL.

Other learning resources reported on campus include the Computer Centre, Central Computing Facility, Central Research Facility and the departmental laboratories. National resources that students of Indian institutes commonly use include NPTEL video courses and the National Digital Library of India; check with the library on which subscriptions MANIT currently holds.

12. Hostels, food and campus services

Hostels
Separate hostels for boys and girls are provided, with a mess and Wi-Fi on campus (Source: aggregators). Wikipedia describes the hostel complex as 9 boys' hostels plus 1 NRI boys' hostel (hostel numbers 1 to 12 except 7 and 12) and 2 girls' hostels (numbers 7 and 12), with a built-up hostel area of 14,011 square metres. Other sources give different counts, such as 7 boys' hostels for about 2,500 students and 2 girls' hostels for about 900 students. The exact number should be taken from the official hostel notice.

• Each hostel is reported to have indoor and outdoor games facilities.
• Registration for the hostel and the mess is done at the time of admission (Source: student review).
• The mess is on the campus and has a student mess committee. Both vegetarian and non-vegetarian food is available (Source: student reviews).
• Student reviews describe the hostel as basic but liveable; some mention weak mobile network in hostels.

Medical and other services
• Dispensary with a Senior Medical Officer and a Medical Officer on the staff list.
• State Bank of India branch and ATM on campus.
• Post office and shopping complex inside the campus.
""",

    # Page 10
    """• Transport to the city is reported by an aggregator; confirm current arrangements with the institute.

13. Student life: fests, societies and sports

Annual festivals
• Technosearch: Annual national-level technical festival with workshops, competitions, seminars and evening shows. Bigger societies host their events within it. Typical timing: October to November (reports vary slightly).
• Maffick: Annual cultural festival with dance, music and other competitions. Described by students as the biggest fest in central India. Typical timing: Reported anywhere from March to July depending on the year.
• Tooryanaad: Annual Hindi literary and cultural fest organised by the Rajbhasha Karyanvayan Samiti, described as the largest Hindi fest at a technical college in India. Timing: Varies.
• Chimera: Annual national-level inter-college quiz competition. Timing: Varies.
• Ripple: Annual literary event. Timing: Varies.
• Chemicarnival: Annual chemical engineering festival. Timing: Varies.
(Sources: Wikipedia, PaGaLGuY, student reviews. Festival sites technosearch.org and maffick.org are listed in Section 20.)

Societies and clubs
• Technical: Vision (technical society running robotics, embedded systems, programming and simulation workshops), IEEE Student Branch, ISTE chapter, Robotics Club, SAE Collegiate Club, Flying Club, Innovation Club, E-Cell.
• Cultural and literary: Roobaroo (cultural society), Editorial Club, Literary clubs, Drama, Music, Movie and Photography clubs, Quizzers Club, Tornado (Hindi literature club).
• Social: Aaroha (NGO), Think India, NCC and other social clubs.
• Rajbhasha Karyanvayan Samiti: official Hindi club set up under constitutional provision, which promotes Hindi through events and campaigns.
• A web and technical committee maintains the institute and festival websites and provides students with short email IDs under the nitb.in domain (Source: Wikipedia mirror).

Student accounts say societies begin recruiting after the first year, and that in the first year students from all departments are mixed into about 10 sections.

Sports
The sports facilities include football, cricket, basketball, volleyball, track and field, badminton, table tennis, chess, carrom, a gymnasium hall and meditation hall (see Section 4).
""",

    # Page 11
    """14. Training and placement

Placements are run by the Training and Placement Cell, which works with department heads, faculty coordinators and a student committee. Internships of different lengths (reported as 2, 6 and 10 months) and pre-placement offers for pre-final and final-year students are part of the process. An aggregator lists placement@manit.ac.in as the cell's email address (unverified). Internships are described as mandatory in the curriculum with industry tie-ups facilitated (Source: aggregators).

Placement figures reported over the years
• 2021: Reported highest package Rs. 32 LPA, 609 students placed (Source: Physics Wallah)
• 2022: Reported highest package Rs. 85.36 LPA, average Rs. 11.55 LPA, 1,012 placed (Source: Physics Wallah)
• 2023: Reported highest package Rs. 82 LPA, average Rs. 15.6 LPA (median about Rs. 10 LPA) (Source: CollegeDekho, others)
• 2025: Reported highest package Rs. 56 LPA, average Rs. 13 to 16 LPA depending on site. Highest offers to CSE and ECE; Electrical got Rs. 55 LPA (Source: Careers360, GetMyUni)
• 2025 (another report): Reported highest package Rs. 85 LPA, average Rs. 27 LPA for Computer Science, 240+ companies, about 80 percent placement rate (Source: Free Press Journal)

• UG and PG: one aggregator reports 873 UG and 194 PG students placed with 200+ companies and 1,012 offers, and PG average and median around Rs. 7.8 LPA and Rs. 8 LPA (MCA falls under PG).
• Branch pattern: Computer Science is consistently reported as the strongest, with average packages roughly Rs. 25 to 27 LPA; Electronics and Electrical follow; Civil and Chemical are lower, around Rs. 8 to 11 LPA on average.
• Reported recruiters: JP Morgan Chase, Deutsche Bank, Oracle, Deloitte, Accenture, Wipro, Jio, Bharti Airtel, SBI Card, Optum, Samsung, Paytm, ZS Associates, Reliance, Vedanta, MSCI, HDFC, EXL, AU Bank and Ola Electric.
• LPA means lakh rupees per annum (1 lakh = 100,000).

These are third-party figures. For decisions, use the official NIRF data submitted by MANIT or the placement report published by the Training and Placement Cell.
""",

    # Page 12
    """15. Rankings and accreditation

NIRF Rankings:
• NIRF 2024, Engineering: Rank 72 (Sources: Wikipedia, JosaaPP)
• NIRF 2024, Architecture and Planning: Rank 17 (Source: JosaaPP)
• NIRF 2025, Engineering: Rank 81 (Source: Shiksha, aggregator)
• NIRF 2025, Architecture and Planning: Rank 17 (Source: Shiksha, aggregator)
• NIRF 2023, Engineering: Rank 60 (Source: QuestionPaper.in, aggregator)

• Approvals and recognition: AICTE approved; UGC recognised; NBA accreditation is mentioned by several listings. One aggregator reports a NAAC A grade in 2023; verify on the NAAC website.
• Ranking positions change every year. NIRF links are in Section 20.

16. Research, centres and Ph.D.

• Centres of Excellence reported: Artificial Intelligence, Smart Manufacturing, Water Resource Management and Cable Technology (Source: Careers360).
• Central facilities: Central Computing Facility, Central Research Facility and a Data Center.
• Research themes mentioned by aggregators: artificial intelligence, material science, renewable energy and cyber security.
• Ph.D. programmes are offered across departments with two admission cycles a year; about 200 seats were reported for Autumn 2026.
• Faculty recruitment is announced on the official website and applications are accepted on the recruitment portal (links in Section 20). Salary follows the 7th Pay Commission scale as stated in the 2024 notice.

17. Administration and contact directory

General contact
Address: Maulana Azad National Institute of Technology, Link Road Number 3, Near Kali Mata Mandir, Bhopal, Madhya Pradesh 462003 (Source: Govt. portal)
Phones: 91-755-4051000, 91-755-4052000, 91-755-2670900 (Source: Govt. portal)
Fax: 91-755-2670562 (Source: Govt. portal)
Public relations office: pro@manit.ac.in (Source: Govt. portal)
Another general address: nsr@manit.ac.in (Source: Govt. portal)

Offices (from public contact directories; verify before relying)
• Registrar: registrar@manit.ac.in, 0755-4051012 (Source: Contact directory)
• Academic section (Assistant Registrar, Academics): academic@manit.ac.in (Source: Contact directory)
• Admissions: admission@manit.ac.in; faculty in-charge phone 0755-4051614 (Sources: NIMCET brochure, contact directory)
• Stores and Purchase: 0755-4051040 (Source: Contact directory)
""",

    # Page 13
    """Office contacts continued:
• Finance and Accounts: 0755-4051042 (Source: Contact directory)
• Central Computing Facility: 0755-4051005 (Source: Contact directory)
• Central Research Facility: 0755-4051006 (Source: Contact directory)
• Training and Placement Cell: placement@manit.ac.in (unverified) (Source: Aggregator)
• General information: info@manit.ac.in (unverified) (Source: Aggregator)

Governance: the institute is run by the Director, with the Registrar as the administrative head, under the Board of Governors and the NIT Council. Names of office holders change often and are not recorded in this handbook; check the official website for current officials.

18. How to reach MANIT

• Location: Link Road Number 3, near Kali Mata Mandir, Bhopal. Approximate coordinates 23.2136 N, 77.3997 E (Source: Wikipedia).
• By air: Raja Bhoj Airport, Bhopal, is the nearest airport, about 15 km from the campus (Source: aggregator).
• By rail: Bhopal is a major railway junction. The two main stations in the city are Bhopal Junction and Rani Kamlapati (formerly Habibganj) station (General knowledge).
• Local transport: auto-rickshaws, taxis and city buses connect the campus with the rest of Bhopal (General knowledge).
• Bhopal is the capital of Madhya Pradesh and is known as the City of Lakes.

19. Notable alumni

People listed by Wikipedia as MANIT alumni include:
• Ajit Jogi, first Chief Minister of Chhattisgarh.
• P. C. Sharma, Cabinet Minister in the Madhya Pradesh government.
• Suresh Pachouri, veteran politician and former Rajya Sabha member.
• Satish Kumar Sharma, chairman and managing director of the Nuclear Power Corporation of India.
• Santosh Choubey, founder and chairman of AISECT and chancellor of the AISECT Group of Universities.
• Rambabu Kodali, pro-vice chancellor of Kalinga Institute of Industrial Technology.
• Naveen Polishetty and Rajeev Verma, film and television actors.
""",

    # Page 14
    """20. Website navigation and URL directory

This section is the lookup table for link questions. Each entry has a topic, search keywords, a link (if one could be verified) and a status. When a user asks for the link to a topic, find the matching entry by its keywords.

IMPORTANT: Many pages were found as references in third-party sources dated 2020 to 2024. The institute's website may have been restructured since then, so a link marked cited_in_sources should be tested before it is shared. Entries marked needs_verification have no known link on purpose; the main website is the fallback.

Links: Core
• MANIT official website (home page)
  Search keywords: manit, nit bhopal, website, home, official site, institute
  Link: https://www.manit.ac.in
  Status: cited_in_sources (Found in third-party sources; re-check that it still opens)
  Note: Main entry point. Most sections below are reachable from its menus.

• About MANIT
  Search keywords: about, about us, overview, institute profile, campus
  Link: http://www.manit.ac.in/about-us
  Status: cited_in_sources (Found in third-party sources; re-check that it still opens)

• History of MANIT
  Search keywords: history, founding, establishment, heritage
  Link: http://www.manit.ac.in/history
  Status: cited_in_sources (Found in third-party sources; re-check that it still opens)

• Undergraduate programmes
  Search keywords: ug, undergraduate, btech, b.tech, barch, b.arch, bplan, b.plan, courses, seats
  Link: http://www.manit.ac.in/ug-program
  Status: cited_in_sources (Found in third-party sources; re-check that it still opens)

• Postgraduate programmes
  Search keywords: pg, postgraduate, mtech, m.tech, mca, mba, mplan, m.plan, msc, seats, intake
  Link: http://www.manit.ac.in/pg-programme?page=1
  Status: cited_in_sources (Found in third-party sources; re-check that it still opens)

Links: Departments
• Architecture and Planning department: http://www.manit.ac.in/architecture-planning
• Biological Science and Engineering department: http://www.manit.ac.in/content/biological-science-engineering
""",

    # Page 15
    """Department Links continued:
• Civil Engineering department: http://www.manit.ac.in/civil-engineering-department
• Chemical Engineering department: http://www.manit.ac.in/content/chemical-engineering-0
• Computer Science and Engineering department: http://www.manit.ac.in/computer-science-engineering-department-0
• Electrical Engineering department: http://www.manit.ac.in/content/electrical-engineering
• Electronics and Communication Engineering department: http://www.manit.ac.in/content/electronics-communication-engineering
• Mechanical Engineering department: http://www.manit.ac.in/content/mechanical-engineering
• Materials Science and Metallurgical Engineering department: http://www.manit.ac.in/content/material-science-metallurgical-engineering-0
• Physics department: http://www.manit.ac.in/content/physics-department
• Chemistry department: http://www.manit.ac.in/content/chemistry-department
• Mathematics (Applied Mathematics) department: http://www.manit.ac.in/content/mathematics-applied-mathematics-department
Note: MCA is run by the department listed in the PG programme list as Mathematics, Bioinformatics and Computer Applications (MBC). This older page may predate that naming; verify the MCA-specific page.
""",

    # Page 16
    """Humanities and Management:
• Humanities department: http://www.manit.ac.in/content/humanities-department
• Department of Management Studies (DMS): http://www.manit.ac.in/content/department-management-studies-dms

Links: Recruitment
• Faculty recruitment notice (2024 cycle): https://www.manit.ac.in/content/faculty-recruitment-2024
• MANIT recruitment portal: http://recruitment.manit.ac.in
• MANIT conference portal: https://conf.manit.ac.in (Note: conference site, not main website)

Links: Student sites
• nitb.in student web domain: http://www.nitb.in (Students receive @nitb.in email addresses)
• Technosearch (annual technical fest): http://www.technosearch.org
• Maffick (annual cultural fest): http://www.maffick.org
• IEEE Student Branch, MANIT: http://ieeenitb.org
""",

    # Page 17
    """Links: National portals
• Council of NITs: http://nitcouncil.org.in
• NIRF 2024 Engineering ranking: https://www.nirfindia.org/Rankings/2024/EngineeringRanking.html
• NIRF 2024 Architecture and Planning ranking: https://www.nirfindia.org/Rankings/2024/ArchitectureRanking.html
• JEE Main (NTA): https://jeemain.nta.ac.in
• NIMCET (MCA entrance, NITs): http://www.nimcet.in
• JoSAA counselling portal: https://josaa.nic.in
• CSAB counselling portal: https://csab.nic.in
• CCMT (M.Tech counselling): https://ccmt.admissions.nic.in
• DASA (NRI / foreign student admissions): https://dasanit.org

Links: Needs verification (Fallback to https://www.manit.ac.in)
• Central Library
• Student ERP / login portal
• Examination results (Reported path: main website > Academic > Examination)
• Academic calendar
• Fee structure and fee payment
• Training and Placement Cell
• Hostel information and allotment
• Scholarships
• Notices, circulars and tenders
• Contact page
• Alumni association
""",

    # Page 18
    """Details for links needing verification:
• Central Library: Fallback: https://www.manit.ac.in. Open the main website and search for 'Library'.
• Student ERP / login portal: Ask the Academic section. Fallback: https://www.manit.ac.in
• Examination results: Reported path: main website > Academic > Examination. Results appear roughly 30-35 days after exams.
• Academic calendar: Fallback: https://www.manit.ac.in
• Fee structure and fee payment: Fees are revised periodically. Use the notice on the official website.
• Training and Placement Cell: An aggregator lists placement@manit.ac.in as cell email (unverified). Fallback: https://www.manit.ac.in
• Hostel information and allotment: Fallback: https://www.manit.ac.in
• Scholarships: Fallback: https://www.manit.ac.in
• Notices, circulars and tenders: Fallback: https://www.manit.ac.in
• Contact page: Details in Section 17. Fallback: https://www.manit.ac.in
• Alumni association: Fallback: https://www.manit.ac.in
""",

    # Page 19
    """21. Frequently asked questions

Q: What is the full form of MANIT?
A: Maulana Azad National Institute of Technology, Bhopal.

Q: When was MANIT established?
A: On 4 September 1960 as Maulana Azad College of Technology; it became an NIT in 2002 and an Institution of National Importance in 2007.

Q: Why is it called Maulana Azad?
A: It is named after Maulana Abul Kalam Azad, independent India's first Minister of Education.

Q: What is the MANIT motto?
A: Education is our soul wealth.

Q: Is MANIT a government institute?
A: Yes. It is fully funded by the Ministry of Education, Government of India, and governed by the NIT Council.

Q: How big is the campus?
A: About 650 acres, one of the largest among NITs.

Q: Where is MANIT located?
A: Link Road Number 3, near Kali Mata Mandir, Bhopal, Madhya Pradesh 462003.

Q: What is the official website of MANIT?
A: https://www.manit.ac.in

Q: Where can I find the library link?
A: No library web address could be verified in this handbook. Open https://www.manit.ac.in and look for the Library entry in the menus or the site search. The Central Library and a Digital Library exist on campus.

Q: How do I check my results?
A: Open https://www.manit.ac.in, go to Academic, then Examination, and choose your result. Results are reported to come out about 30 to 35 days after exams.

Q: Which entrance exam is needed for the MCA?
A: NIMCET (NIT MCA Common Entrance Test).

Q: How long is the MCA at MANIT?
A: Three years, or six semesters.
""",

    # Page 20
    """Frequently asked questions continued:

Q: How many MCA seats are there?
A: 115 in the 2022-23 listing; older sources say 60. Check the current NIMCET seat matrix.

Q: Since when has MANIT offered an MCA?
A: Since 1988.

Q: Which department runs the MCA?
A: Mathematics, Bioinformatics and Computer Applications (MBC).

Q: What are the MCA fees?
A: About Rs. 1.0 lakh in the first year (Rs. 56,500 plus Rs. 43,500) according to one aggregator, excluding hostel and mess. Confirm on the official fee notice.

Q: How is admission done for B.Tech?
A: Through JEE Main and then JoSAA or CSAB counselling.

Q: How is admission done for M.Tech?
A: Through GATE and then CCMT counselling.

Q: How is admission done for the MBA?
A: Through CAT, MAT or CMAT followed by a group discussion and interview.

Q: How is admission done for Ph.D.?
A: Through an institute-level application, entrance test and interview, held twice a year.

Q: Which exam do NRI and foreign students use?
A: DASA, with SAT Subject Test scores, and ICCR scholarship routes.

Q: How many hostels are there?
A: Wikipedia lists 9 boys, 1 NRI boys and 2 girls hostels; other sources give 7 boys and 2 girls hostels. Check the hostel notice.

Q: Is there a medical facility on campus?
A: Yes, a dispensary with a Senior Medical Officer and a Medical Officer.

Q: Is there a bank or ATM on campus?
A: Yes. A State Bank of India branch with an ATM operates from the main campus.

Q: Which are the main fests?
A: Technosearch (technical), Maffick (cultural) and Tooryanaad (Hindi literary and cultural).

Q: When is Technosearch held?
A: Usually October to November.

Q: What is nitb.in?
A: A domain used for institute and student websites; students are reported to get @nitb.in email IDs.

Q: What is the highest placement package?
A: Reports vary by year: Rs. 85.36 LPA (2022), Rs. 82 LPA (2023), Rs. 56 LPA in several 2025 reports. See Section 14.
""",

    # Page 21
    """Frequently asked questions continued:

Q: What is MANIT's NIRF rank?
A: Engineering rank 72 in NIRF 2024; Architecture rank 17. An aggregator reports engineering rank 81 in NIRF 2025.

Q: How far is the airport?
A: Raja Bhoj Airport is about 15 km from the campus.

Q: How do I apply for faculty jobs?
A: Through the recruitment portal at http://recruitment.manit.ac.in.

Q: Whom do I contact for admissions?
A: admission@manit.ac.in, or the general phone numbers 91-755-4051000 and 91-755-2670900.

Q: Is the academic ordinance included here?
A: No. MANIT's own ordinance could not be retrieved, so questions about attendance limits, grading scale and backlog rules should be answered by the Academic section.

Q: Who are some famous alumni?
A: Ajit Jogi, P. C. Sharma, Suresh Pachouri, Satish Kumar Sharma and Santosh Choubey, among others (see Section 19).

22. Glossary of acronyms

MANIT / NIT-B: Maulana Azad National Institute of Technology, Bhopal
MACT: Maulana Azad College of Technology, MANIT's original name
REC: Regional Engineering College, the earlier name of the NITs
NIT Act: National Institutes of Technology Act, 2007, which made NITs Institutions of National Importance
NIT Council: Governing council of the NIT system
NIMCET: NIT MCA Common Entrance Test
JEE Main: Joint Entrance Examination (Main), conducted by the NTA
NTA: National Testing Agency
JoSAA: Joint Seat Allocation Authority, which runs counselling for IITs, NITs, IIITs and GFTIs
CSAB: Central Seat Allocation Board, which runs special and later rounds
CCMT: Centralized Counselling for M.Tech, M.Arch and M.Plan
GATE: Graduate Aptitude Test in Engineering
DASA: Direct Admission of Students Abroad
ICCR: Indian Council for Cultural Relations
TEQIP: Technical Education Quality Improvement Programme (World Bank assisted)
NIRF: National Institutional Ranking Framework
NAAC / NBA: National Assessment and Accreditation Council / National Board of Accreditation
AICTE / UGC: All India Council for Technical Education / University Grants Commission
MBC: Mathematics, Bioinformatics and Computer Applications department
DMS: Department of Management Studies
""",

    # Page 22
    """Glossary of acronyms continued:
SAC: Student Activity Centre
SGPA / CGPA: Semester / Cumulative Grade Point Average
LPA: Lakh rupees per annum (1 lakh = 100,000)
PPO: Pre-placement offer
EWS / OBC-NCL / SC / ST: Economically Weaker Section / Other Backward Classes (non-creamy layer) / Scheduled Caste / Scheduled Tribe
GD / PI: Group Discussion / Personal Interview

23. Known data conflicts and verification checklist

The following items differ between sources. A chatbot should present these as ranges and should not claim a single exact figure.

Topic: MCA duration
What the sources say: 3 years (Wikipedia, PG list) versus 2 years (one aggregator)
Best guidance: Use 3 years

Topic: MCA seats
What the sources say: 115 (2022-23 PG list, NIMCET table) versus 60 (older listings)
Best guidance: Check current seat matrix

Topic: Number of departments
What the sources say: 11 plus 4 schools, 14, or 17
Best guidance: Say about 14, with caveat

Topic: Hostels
What the sources say: 9 boys + 1 NRI + 2 girls (Wikipedia) versus 7 boys + 2 girls
Best guidance: Check hostel notice

Topic: Placement highest package
What the sources say: Rs. 56, 82, 85 or 85.36 LPA depending on year and site
Best guidance: Quote with year and source

Topic: Fees
What the sources say: Different annual and total figures across aggregators
Best guidance: Quote as indicative

Topic: NIRF engineering rank
What the sources say: 60 (2023), 72 (2024), 81 (2025)
Best guidance: Quote with the year

Topic: conf.manit.ac.in
What the sources say: One aggregator lists it as the official website
Best guidance: It looks like a conference site; main site is manit.ac.in

Verification checklist before publishing the chatbot
• Open every cited_in_sources link in a browser and update or remove the ones that fail.
• Find the real library, ERP, results, fee, hostel and placement-cell links from the main website and fill them into manit_links.json.
• Add MANIT's official MCA scheme and syllabus, academic ordinance, academic calendar and fee notice PDFs to the corpus.
• Refresh placement and ranking numbers from the official NIRF submission and the placement report.
"""
]


def build_pdf():
    OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    doc = fitz.open()

    for idx, page_text in enumerate(PAGES, start=1):
        page = doc.new_page(width=595, height=842)  # A4 size
        rect = fitz.Rect(54, 54, 541, 788)
        rc = page.insert_textbox(rect, page_text.strip(), fontsize=10, fontname="helv", color=(0.1, 0.1, 0.1))
        if rc < 0:
            print(f"Warning: Text overflow on page {idx}")

    doc.save(str(OUTPUT_PDF))
    doc.close()
    print(f"Created {len(PAGES)}-page PDF at: {OUTPUT_PDF}")


if __name__ == "__main__":
    build_pdf()

