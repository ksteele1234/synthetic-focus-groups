#!/usr/bin/env python3
"""
Sample detailed personas demonstrating the complete buyer persona structure.
These personas follow the same depth as the Nashville Nick example.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from models.persona import Persona


def create_sarah_marketing_maven():
    """Create Sarah Johnson - The Marketing Maven detailed persona."""
    
    return Persona(
        # 1. Buyer Avatar Basics
        name="Sarah Johnson",
        age=32,
        gender="Female", 
        education="MBA in Marketing",
        relationship_family="Married to David (software engineer), 2 kids - Emma (8) and Jake (5)",
        occupation="Digital Marketing Agency Owner",
        annual_income="$85,000 (goal: $150,000)",
        location="Austin, TX",
        
        # 2. Psychographics & Lifestyle
        hobbies=["Yoga at sunrise", "Reading marketing blogs", "Networking events", "Family camping trips"],
        community_involvement=["PTA Vice President", "Local Women Entrepreneurs Group", "Austin Marketing Meetup organizer"],
        personality_traits=["Analytical", "Perfectionist", "Cost-conscious", "Quality-focused", "Relationship-builder"],
        values=["Family first", "Authentic connections", "Excellence", "Financial independence", "Work-life balance"],
        free_time_activities="Weekend family time, evening marketing research, early morning yoga sessions",
        lifestyle_description="Busy working mom juggling business growth with family priorities. Always looking for efficiency and systems that give her more time with her kids while growing her agency.",
        
        # 3. Pains & Challenges
        major_struggles=[
            "Limited marketing budget stretching across multiple client needs",
            "Time management between client work and business development", 
            "Client acquisition consistency - feast or famine cycles",
            "Competing with larger agencies on price while maintaining quality",
            "Managing cash flow with irregular client payments"
        ],
        obstacles=[
            "Small team capacity constraints",
            "Technology learning curve with new tools",
            "Client education on marketing value",
            "Scaling operations without losing personal touch"
        ],
        why_problems_exist="Running a small agency means wearing all hats - CEO, salesperson, account manager, and mom. There's never enough time or budget to do everything perfectly.",
        
        # 4. Fears & Relationship Impact
        deep_fears_business=[
            "Business failure leading to financial instability",
            "Losing major clients and not being able to pay employees", 
            "Being seen as 'just another small agency'",
            "Cash flow crisis affecting family security",
            "Having to close the agency and work for someone else"
        ],
        deep_fears_personal=[
            "Not being present enough for my children's milestones",
            "Marriage strain from work stress and long hours",
            "Setting a bad example of work-life balance for my kids"
        ],
        fear_impact_spouse="David worries about my stress levels and often has to handle more parenting duties when I'm overwhelmed with client work",
        fear_impact_kids="Emma has started asking why mommy works so much, and Jake acts out when I miss his soccer games for client meetings",
        fear_impact_employees="My stress affects team morale - when I'm anxious about cash flow, everyone feels it",
        fear_impact_clients="When I'm overwhelmed, client communication suffers and they start questioning our capabilities",
        potential_remarks_from_others=[
            "'Sarah's agency is too small to handle our enterprise needs'",
            "'She's spread too thin to give us proper attention'",
            "'Maybe she should just work for a big agency instead of struggling on her own'"
        ],
        
        # 5. Previous Attempts & Frustrations
        previous_agencies_tried=["Local marketing consultants", "Freelancers from Upwork", "Previous agency partnerships"],
        previous_software_tried=["HubSpot", "Mailchimp", "Canva Pro", "Hootsuite", "Google Workspace", "QuickBooks"],
        diy_approaches_tried=["Manual social media posting", "Homemade project management systems", "Excel-based client reporting", "Cold calling campaigns"],
        why_agencies_failed="Other agencies were either too expensive, didn't understand small business needs, or provided cookie-cutter solutions without personal attention",
        why_software_failed="Tools were either too complex for my team to adopt quickly, too expensive for our budget, or didn't integrate well together creating more work instead of less",
        why_diy_failed="Everything took too long and looked unprofessional. I was spending more time on admin tasks than growing the business or serving clients.",
        
        # 6. Desired Outcomes (Practical & Emotional)
        tangible_business_results=[
            "30% revenue growth within 12 months",
            "Streamlined client onboarding reducing setup time by 50%",
            "Automated reporting saving 10 hours per week",
            "Better cash flow predictability",
            "Team efficiency improvements allowing 4-day work weeks"
        ],
        tangible_personal_results=[
            "Home by 6 PM for family dinner every night",
            "Attending all of Emma and Jake's school events", 
            "Weekend family time without work interruptions",
            "Monthly date nights with David",
            "Annual family vacation without work calls"
        ],
        emotional_transformations=[
            "Feeling confident and in control of the business",
            "Peace of mind about financial security",
            "Pride in building something meaningful",
            "Joy in work without guilt about family time",
            "Excitement about the future instead of constant worry"
        ],
        if_only_soundbites=[
            "If only I could automate my marketing processes... it would mean I could focus on strategy and family instead of daily tasks",
            "If only I had reliable systems... it would mean I could sleep better knowing everything is handled",
            "If only clients could see our value clearly... it would mean no more justifying every expense"
        ],
        
        # 7. Hopes & Dreams  
        professional_recognition_goals=[
            "Featured in Austin Business Journal as 'Entrepreneur to Watch'",
            "Speaking at marketing conferences about small agency success",
            "Recognition as Austin's go-to boutique marketing agency"
        ],
        financial_freedom_goals=[
            "Six-figure consistent monthly revenue",
            "Emergency fund covering 12 months of expenses",
            "College funds fully funded for both kids",
            "Investment portfolio building passive income"
        ],
        lifestyle_upgrade_goals=[
            "Larger home office space for the growing team",
            "Family lake house for weekends and retreats",
            "European family vacation every other year",
            "Tesla Model Y for environmental and style reasons"
        ],
        family_legacy_goals=[
            "Building a business Emma and Jake can be proud of",
            "Teaching them entrepreneurship and work ethic",
            "Creating generational wealth for the family"
        ],
        big_picture_aspirations="Build a marketing agency that runs smoothly without me micromanaging everything, so I can spend quality time with my children while they're young, and create a legacy business that provides financial freedom for my family.",
        
        # 8. How They Want to Be Seen by Others
        desired_reputation=[
            "The go-to marketing expert for small businesses in Austin",
            "A successful working mom who has it all figured out",
            "Someone who delivers exceptional results with personal attention",
            "A trusted advisor and strategic partner, not just a vendor"
        ],
        success_statements_from_others=[
            "'Sarah transformed our business - revenue doubled in 6 months'",
            "'She somehow manages to be an amazing mom AND run a thriving agency'", 
            "'Sarah's team feels like an extension of our company'",
            "'I wish I could clone Sarah for all my business needs'"
        ],
        
        # 9. Unwanted Outcomes
        things_to_avoid=[
            "Wasting money on tools that don't integrate or deliver ROI",
            "Overwhelming complexity that requires extensive training",
            "Time-consuming setup processes that delay results", 
            "Vendor relationships that feel impersonal or pushy",
            "Solutions that work initially but break down under scale"
        ],
        unwanted_quotes=[
            "'This is too complicated - I don't have time to learn another system'",
            "'Great, another tool that doesn't talk to the others'",
            "'The setup time is longer than doing it manually'",
            "'This is supposed to save time but I'm working more than ever'"
        ],
        
        # 10. Summary
        persona_summary="Sarah Johnson is a 32-year-old female digital marketing agency owner from Austin, TX, married with two kids. She struggles with limited budgets, time management, and scaling her business while maintaining work-life balance. Her primary goals are 30% revenue growth and better family time. Personality: analytical, perfectionist, cost-conscious.",
        
        # 11. Day-in-the-Life Scenario (Ideal Future State)
        ideal_day_scenario="""
        6:00 AM - Wake up refreshed, no anxiety about what fires need fighting today
        6:30 AM - Yoga and meditation, knowing all systems are running smoothly
        7:30 AM - Family breakfast, fully present with Emma and Jake
        8:30 AM - Kids to school, quality time with David over coffee
        9:00 AM - Arrive at office, automated reports show all clients on track
        9:30 AM - Strategic planning session with team, focusing on growth not firefighting
        11:00 AM - New client presentation, confident in our automated processes
        12:30 PM - Lunch with networking group, no urgent client emails interrupting
        2:00 PM - Creative strategy session, energized and focused
        4:00 PM - Review automated client reports - everything green
        5:00 PM - Team wrap-up, everyone leaving on time and satisfied
        6:00 PM - Home for family dinner, work phone stays in the office
        7:30 PM - Help kids with homework, attend Jake's soccer practice
        9:00 PM - Quality time with David, discussing weekend family plans not work stress
        10:30 PM - Reading for pleasure, peaceful mind knowing tomorrow is organized
        """
    )


def create_mike_growth_hacker():
    """Create Mike Rodriguez - The Growth Hacker detailed persona."""
    
    return Persona(
        # 1. Buyer Avatar Basics
        name="Mike Rodriguez", 
        age=28,
        gender="Male",
        education="Bachelor's in Business Administration, Google Analytics Certified",
        relationship_family="Single, dating Jessica (teacher) for 2 years, considering engagement",
        occupation="Marketing Manager at TechFlow Solutions (B2B SaaS, 200 employees)",
        annual_income="$65,000 (goal: $90,000+ as VP of Marketing)",
        location="Seattle, WA",
        
        # 2. Psychographics & Lifestyle
        hobbies=["Gaming (strategy games)", "Hiking Pacific Northwest trails", "Tech meetups", "Coffee shop working", "Basketball with college friends"],
        community_involvement=["Seattle Young Professionals Network", "TechFlow volunteer mentor program", "Local marketing meetup speaker"],
        personality_traits=["Data-driven", "Competitive", "Collaborative", "Results-oriented", "Ambitious", "Detail-oriented"],
        values=["Meritocracy", "Continuous learning", "Transparency", "Innovation", "Team success"],
        free_time_activities="Weekend hiking with Jessica, evening gaming sessions, Saturday morning basketball, Sunday coffee shop laptop sessions for side projects",
        lifestyle_description="Urban professional who thrives on growth metrics and team wins. Always learning new marketing tactics, looking for the next promotion, and building a reputation in Seattle's tech scene.",
        
        # 3. Pains & Challenges
        major_struggles=[
            "Proving clear ROI to skeptical executives who don't understand marketing attribution",
            "Data silos between marketing tools making reporting a nightmare",
            "Team collaboration challenges with remote developers and sales",
            "Getting buy-in for new marketing technologies from conservative IT department",
            "Balancing short-term lead gen pressure with long-term brand building"
        ],
        obstacles=[
            "Legacy CRM system that doesn't integrate with modern marketing tools",
            "Limited budget approval authority - everything needs executive sign-off",
            "Sales team resistance to new lead qualification processes",
            "Competing priorities between different department heads"
        ],
        why_problems_exist="Mid-size company growing pains - we're too big for simple solutions but too small for enterprise-level resources. Everyone wants results but nobody wants to invest in proper systems.",
        
        # 4. Fears & Relationship Impact
        deep_fears_business=[
            "Missing quarterly targets and being seen as ineffective",
            "Getting passed over for promotion to VP of Marketing", 
            "Being blamed for poor lead quality when sales processes are broken",
            "Layoffs hitting marketing team first during economic downturns",
            "Technology choices I recommend failing and damaging my credibility"
        ],
        deep_fears_personal=[
            "Career stagnation while peers advance at other companies",
            "Not being financially ready for engagement/marriage with Jessica",
            "Imposter syndrome - am I really VP-level material?",
            "Work stress affecting relationship with Jessica"
        ],
        fear_impact_spouse="Jessica worries about my long hours and weekend work stress. She's started hinting that I seem more excited about work achievements than our relationship milestones",
        fear_impact_employees="My team feeds off my energy - when I'm stressed about numbers, they work longer hours and burn out faster",
        fear_impact_peers="Other department heads lose confidence in marketing's ability to drive results, making collaboration harder",
        fear_impact_clients="When attribution is unclear, customer success team questions marketing's contribution to renewals and expansions",
        potential_remarks_from_others=[
            "'Mike talks about data but can't prove marketing's impact on revenue'",
            "'He's good with tools but doesn't understand the business strategy'",
            "'Maybe we need someone more senior to run marketing'"
        ],
        
        # 5. Previous Attempts & Frustrations
        previous_agencies_tried=["Digital marketing consultants for paid ads", "Content marketing agency", "Marketing automation specialists"],
        previous_software_tried=["HubSpot", "Salesforce", "Google Analytics", "Mixpanel", "Slack", "Asana", "Marketo trial", "Pardot demo"],
        diy_approaches_tried=["Excel-based attribution modeling", "Manual lead scoring in spreadsheets", "Custom Google Data Studio dashboards", "Home-grown Slack bot for notifications"],
        why_agencies_failed="Agencies didn't understand our technical product or B2B sales cycle. They optimized for vanity metrics instead of revenue impact. Communication was poor and results were generic.",
        why_software_failed="Tools don't integrate well together making reporting a manual nightmare. Data sits in silos. Training the team on new platforms takes too long and they revert to old habits.",
        why_diy_failed="Everything breaks when people leave or processes change. Takes too much time to maintain. Looks unprofessional in executive presentations. Doesn't scale with team growth.",
        
        # 6. Desired Outcomes (Practical & Emotional)
        tangible_business_results=[
            "Clear multi-touch attribution showing marketing's revenue contribution",
            "40% increase in qualified leads within 6 months", 
            "Marketing and sales alignment on lead definition and handoff process",
            "Automated reporting reducing manual work by 75%",
            "Executive dashboard showing real-time marketing ROI"
        ],
        tangible_personal_results=[
            "Promotion to VP of Marketing within 18 months",
            "Salary increase to $90,000+ range",
            "Recognition as key contributor to company growth",
            "Industry speaking opportunities building personal brand",
            "More predictable work schedule for better work-life balance"
        ],
        emotional_transformations=[
            "Confidence in marketing's strategic value and my leadership",
            "Pride in data-driven decisions and measurable impact",
            "Excitement about marketing possibilities instead of constant firefighting",
            "Respect from executive team and sales colleagues",
            "Peace of mind about career trajectory and financial future"
        ],
        if_only_soundbites=[
            "If only I could prove clear ROI to executives... it would mean job security and the promotion I've been working toward",
            "If only our tools talked to each other... it would mean I could focus on strategy instead of data cleanup",
            "If only sales trusted our lead quality... it would mean true marketing and sales alignment"
        ],
        
        # 7. Hopes & Dreams
        professional_recognition_goals=[
            "VP of Marketing title at a high-growth startup",
            "Speaking at SaaStr or similar industry conferences",
            "Featured in marketing publications for innovative attribution strategies",
            "Building Seattle's most data-driven marketing team"
        ],
        financial_freedom_goals=[
            "$100,000+ salary with equity upside", 
            "Emergency fund for career transitions",
            "Engagement ring budget without financial stress",
            "Investment in rental property or tech stocks"
        ],
        lifestyle_upgrade_goals=[
            "Downtown Seattle condo with city views",
            "Engagement and wedding with Jessica",
            "European honeymoon without work interruptions",
            "New car to replace aging Honda Civic"
        ],
        family_legacy_goals=[
            "Building reputation as a marketing leader in Seattle",
            "Mentoring junior marketers like others mentored me",
            "Financial stability to start a family with Jessica"
        ],
        big_picture_aspirations="Become a VP of Marketing at a high-growth Seattle startup where I can build a world-class marketing team, prove marketing's strategic value through clear attribution, and earn the recognition and compensation that matches my contributions to company growth.",
        
        # 8. How They Want to Be Seen by Others
        desired_reputation=[
            "The data guy who actually drives revenue, not just metrics",
            "Rising star in Seattle's marketing community", 
            "The marketing manager who finally cracked attribution",
            "Team player who lifts everyone up while achieving results"
        ],
        success_statements_from_others=[
            "'Mike transformed how we think about marketing ROI'",
            "'He's the reason our sales and marketing teams actually work together now'",
            "'Best hire we've made - marketing finally feels strategic'", 
            "'Mike's attribution model became the template for the entire industry'"
        ],
        
        # 9. Unwanted Outcomes
        things_to_avoid=[
            "Another tool that promises integration but delivers manual workarounds",
            "Complex attribution models that no one else can understand or maintain",
            "Solutions that work for big enterprises but overwhelm our mid-size team",
            "Vendor relationships that disappear after the sale",
            "Technology choices that lock us into one ecosystem"
        ],
        unwanted_quotes=[
            "'This attribution model is too complicated - just show me lead numbers'",
            "'We spent six months implementing this and we're still doing manual reports'", 
            "'Mike's fancy dashboard is pretty but it doesn't help us close deals'",
            "'Another marketing tool that promised the world and delivered confusion'"
        ],
        
        # 10. Summary
        persona_summary="Mike Rodriguez is a 28-year-old male marketing manager at a B2B SaaS company in Seattle, single but in a serious relationship. He struggles with proving marketing ROI, data silos, and team collaboration. His primary goals are VP-level promotion and clear attribution modeling. Personality: data-driven, competitive, collaborative.",
        
        # 11. Day-in-the-Life Scenario (Ideal Future State)
        ideal_day_scenario="""
        7:00 AM - Wake up energized, excited to check yesterday's automated performance reports
        7:30 AM - Coffee while reviewing executive dashboard - all metrics trending up
        8:30 AM - Quick workout at company gym, networking with other department heads
        9:30 AM - Team standup, everyone aligned on data-driven priorities
        10:00 AM - Executive meeting presenting clear attribution data showing marketing's 35% contribution to pipeline
        11:00 AM - Sales partnership session, reviewing qualified leads with full context and handoff notes
        12:30 PM - Lunch interview with marketing publication about our attribution breakthrough
        2:00 PM - Strategic planning with CFO, confident in budget requests backed by ROI data
        3:30 PM - 1:1 mentoring with junior team member, sharing growth opportunities
        4:30 PM - Review automated reports, spot trends and optimization opportunities
        5:30 PM - Leave office knowing all systems are working and team is thriving
        7:00 PM - Dinner with Jessica, fully present and excited about weekend plans
        8:30 PM - Gaming session with friends, mind clear from work stress
        10:00 PM - Reading marketing strategy book, excited about tomorrow's possibilities
        """
    )


def create_jenny_scaling_solopreneur():
    """Create Jenny Chen - The Scaling Solopreneur detailed persona."""
    
    return Persona(
        # 1. Buyer Avatar Basics
        name="Jennifer 'Jenny' Chen",
        age=35,
        gender="Female", 
        education="Bachelor's in Communications, Google Ads & Facebook Blueprint Certified",
        relationship_family="Divorced from Mark (amicable), co-parenting daughter Lily (10)",
        occupation="Freelance Social Media Manager & Content Strategist",
        annual_income="$48,000 (irregular, goal: $75,000 stable)",
        location="San Francisco, CA",
        
        # 2. Psychographics & Lifestyle  
        hobbies=["Photography (especially food and lifestyle)", "Coffee shop hopping", "Online freelancer community groups", "Weekend farmers markets with Lily"],
        community_involvement=["SF Freelancers Union member", "Lily's school parent volunteer", "Local photography meetup organizer", "Women's entrepreneur support group"],
        personality_traits=["Creative", "Detail-oriented", "Client-focused", "Resourceful", "Independent", "Perfectionist"],
        values=["Financial independence", "Flexibility for parenting", "Creative fulfillment", "Authentic relationships", "Quality over quantity"],
        free_time_activities="Saturday photography walks, Sunday morning coffee shop work sessions, evening client work after Lily's bedtime, weekend adventures with Lily",
        lifestyle_description="Single mom balancing freelance hustle with quality parenting time. Always optimizing for efficiency and client satisfaction while building toward scalable business model. Craves stability but values freedom.",
        
        # 3. Pains & Challenges
        major_struggles=[
            "Inconsistent income creating financial stress and planning challenges",
            "Client reporting overhead eating 15+ hours per week", 
            "Work-life balance when clients expect 24/7 availability",
            "Competing with agencies on price while maintaining boutique quality",
            "Scaling services without losing personal touch that clients love"
        ],
        obstacles=[
            "Lack of professional team support for larger projects",
            "Client education on social media ROI and realistic expectations",
            "Cash flow gaps between project payments",
            "Technology overwhelm with constant platform changes",
            "Single parenting responsibilities limiting networking and growth opportunities"
        ],
        why_problems_exist="Freelancing means doing everything myself - client acquisition, project delivery, admin, accounting, and parenting. There's never enough time or systems to do it all professionally.",
        
        # 4. Fears & Relationship Impact
        deep_fears_business=[
            "Losing major clients and not being able to pay rent",
            "Being seen as 'just a freelancer' instead of strategic partner",
            "Technology changes making my skills obsolete", 
            "Burnout leading to client dissatisfaction and business collapse",
            "Never being able to scale beyond trading time for money"
        ],
        deep_fears_personal=[
            "Financial instability affecting Lily's opportunities and security",
            "Working so much that I miss Lily's childhood milestones",
            "Not being a good role model for work-life balance",
            "Never finding financial security or romantic partnership again"
        ],
        fear_impact_kids="Lily sometimes acts out when I'm stressed about money or working late nights. She's asked why other kids' parents have 'real jobs' and seem less worried",
        fear_impact_clients="When I'm overwhelmed, I overdeliver to compensate, setting unrealistic expectations and burning out faster",
        fear_impact_peers="Other freelancers see my stress and question if this lifestyle is sustainable long-term", 
        potential_remarks_from_others=[
            "'Jenny's good but she's just one person - what if she gets sick or overwhelmed?'",
            "'She's too focused on perfectionism to scale efficiently'",
            "'Maybe she should just get a regular job with benefits for stability'"
        ],
        
        # 5. Previous Attempts & Frustrations
        previous_agencies_tried=["Marketing agency partnerships", "Subcontracting for larger agencies", "Referral partnerships with other freelancers"],
        previous_software_tried=["Buffer", "Hootsuite", "Later", "Sprout Social", "Canva Pro", "Adobe Creative Suite", "Monday.com", "FreshBooks"],
        diy_approaches_tried=["Excel-based client reporting", "Manual social media scheduling", "DIY client onboarding packets", "Homemade project management systems"],
        why_agencies_failed="Agencies treated me like a contractor, not a partner. Pay was inconsistent and I had no control over client relationships. They took credit for my strategic work.",
        why_software_failed="Tools either lacked features I needed, were too expensive for irregular income, or created more work instead of saving time. Reporting was still mostly manual.",
        why_diy_failed="Everything looked unprofessional compared to what clients expected. Time-intensive processes didn't scale. Clients questioned my credibility with homemade solutions.",
        
        # 6. Desired Outcomes (Practical & Emotional)
        tangible_business_results=[
            "Stable monthly income of $6,000+ through retainer clients",
            "Automated client reporting saving 10-12 hours weekly",
            "Streamlined client onboarding reducing setup time by 60%",
            "Professional service packages allowing premium pricing",
            "Referral system generating 30% of new business automatically"
        ],
        tangible_personal_results=[
            "Predictable schedule allowing quality time with Lily",
            "Financial security for Lily's college fund and activities",
            "Professional reputation attracting better clients",
            "Time for dating and building adult relationships",
            "Emergency fund reducing financial anxiety"
        ],
        emotional_transformations=[
            "Confidence in my value as a strategic partner, not just execution",
            "Pride in building a sustainable business model",
            "Peace of mind about financial stability",
            "Excitement about business growth instead of survival mode",
            "Joy in work without guilt about time away from Lily"
        ],
        if_only_soundbites=[
            "If only I could automate client reporting... it would mean I could focus on strategy and spend evenings with Lily instead of spreadsheets",
            "If only I had stable retainer income... it would mean financial security for Lily's future and my peace of mind",
            "If only clients saw me as a strategic partner... it would mean premium pricing and respect for boundaries"
        ],
        
        # 7. Hopes & Dreams
        professional_recognition_goals=[
            "Featured in freelancer success stories and publications",
            "Speaking at social media and freelancer conferences",
            "Building the go-to boutique social media consultancy in SF",
            "Mentoring other single parents in freelancing"
        ],
        financial_freedom_goals=[
            "Six-figure annual income with predictable monthly cash flow",
            "Emergency fund covering 12 months of expenses",
            "Lily's college fund fully funded by her 16th birthday",
            "Investment portfolio building passive income"
        ],
        lifestyle_upgrade_goals=[
            "Two-bedroom apartment in better school district for Lily",
            "Reliable car replacing aging Honda with constant repairs",
            "Annual mother-daughter vacation without work stress",
            "Professional photography equipment for personal creative projects"
        ],
        family_legacy_goals=[
            "Showing Lily that women can build successful businesses",
            "Financial stability providing opportunities I didn't have",
            "Building a business that could support both of us long-term"
        ],
        big_picture_aspirations="Build a boutique social media consultancy that generates stable six-figure income through retainer relationships, allowing me to provide financial security for Lily while maintaining the flexibility to be present for her childhood and pursue creative fulfillment.",
        
        # 8. How They Want to Be Seen by Others
        desired_reputation=[
            "The social media strategist who delivers results and maintains boundaries",
            "Successful single mom entrepreneur who has it figured out",
            "Creative professional who brings fresh ideas and reliable execution",
            "Trusted advisor who understands small business challenges"
        ],
        success_statements_from_others=[
            "'Jenny transformed our social media presence and taught us to think strategically'",
            "'She's proof that you can build a successful business while being an amazing mom'",
            "'Jenny's reporting helped us understand ROI for the first time'",
            "'I trust Jenny completely - she's become essential to our marketing success'"
        ],
        
        # 9. Unwanted Outcomes
        things_to_avoid=[
            "Complex tools requiring extensive training when I need quick wins",
            "Monthly subscriptions that strain inconsistent cash flow",
            "Solutions that create more client questions instead of demonstrating value",
            "Platforms that change features constantly requiring relearning",
            "Tools that make my work look automated instead of strategic"
        ],
        unwanted_quotes=[
            "'This looks too automated - where's the personal touch we're paying for?'",
            "'Jenny used to be responsive but now everything goes through some system'",
            "'These reports are fancy but I don't understand what they mean for my business'",
            "'She's gotten too big for her britches - maybe we need someone who needs our business more'"
        ],
        
        # 10. Summary
        persona_summary="Jennifer Chen is a 35-year-old divorced female freelance social media manager from San Francisco, co-parenting a 10-year-old daughter. She struggles with inconsistent income, client reporting overhead, and work-life balance. Her primary goals are stable monthly income and automated reporting. Personality: creative, detail-oriented, client-focused.",
        
        # 11. Day-in-the-Life Scenario (Ideal Future State)
        ideal_day_scenario="""
        6:30 AM - Wake up refreshed, no anxiety about client deliverables or cash flow
        7:00 AM - Coffee while reviewing automated overnight reports - all clients trending positive  
        8:00 AM - Quality breakfast with Lily, helping with homework and listening to her stories
        8:45 AM - Walk Lily to school, present and engaged without work phone distractions
        9:30 AM - Arrive at coffee shop office, automated reports already sent to all clients
        10:00 AM - Strategic consultation call with potential retainer client, confident in premium pricing
        11:30 AM - Creative content brainstorming session, energized by clear boundaries and good systems
        1:00 PM - Lunch with freelancer friend, sharing success stories instead of survival struggles  
        2:30 PM - Client strategy session, focused on growth instead of firefighting
        4:00 PM - Wrap up work knowing automated systems are handling routine tasks
        4:30 PM - Pick up Lily from school, fully present for her day's adventures
        6:00 PM - Cooking dinner together, relaxed knowing tomorrow is organized
        8:00 PM - Family time and bedtime routine, no laptop in sight
        9:30 PM - Personal time - photography, reading, or connecting with adult friends
        10:30 PM - Peaceful sleep knowing the business runs smoothly and Lily is thriving
        """
    )


if __name__ == "__main__":
    print("🎭 DETAILED PERSONA EXAMPLES")
    print("=" * 60)
    
    # Create the detailed personas
    sarah = create_sarah_marketing_maven()
    mike = create_mike_growth_hacker() 
    jenny = create_jenny_scaling_solopreneur()
    
    personas = [sarah, mike, jenny]
    
    for persona in personas:
        print(f"\n📋 {persona.name} - {persona.occupation}")
        print("-" * 40)
        print(f"Age: {persona.age} | Location: {persona.location}")
        print(f"Income: {persona.annual_income}")
        print(f"Family: {persona.relationship_family}")
        print(f"\nMajor Struggles:")
        for struggle in persona.major_struggles[:3]:
            print(f"  • {struggle}")
        print(f"\nDeep Fears:")
        for fear in persona.deep_fears_business[:2]:
            print(f"  • {fear}")
        print(f"\nDesired Outcomes:")
        for outcome in persona.tangible_business_results[:2]:
            print(f"  • {outcome}")
        print(f"\nSignature Phrase:")
        if persona.if_only_soundbites:
            print(f"  \"{persona.if_only_soundbites[0]}\"")
    
    print(f"\n✅ Created {len(personas)} detailed personas with full buyer psychology profiles")
    print("📄 Each persona includes all 11 sections:")
    print("   1. Buyer Avatar Basics")
    print("   2. Psychographics & Lifestyle") 
    print("   3. Pains & Challenges")
    print("   4. Fears & Relationship Impact")
    print("   5. Previous Attempts & Frustrations")
    print("   6. Desired Outcomes (Practical & Emotional)")
    print("   7. Hopes & Dreams")
    print("   8. How They Want to Be Seen by Others")
    print("   9. Unwanted Outcomes")
    print("   10. Summary")
    print("   11. Day-in-the-Life Scenario")
    
    # Test persona prompt generation
    print(f"\n🤖 Testing AI prompt generation for {sarah.name}...")
    prompt = sarah._generate_detailed_prompt()
    print(f"Generated prompt length: {len(prompt)} characters")
    print(f"✅ Rich persona context ready for AI agents")