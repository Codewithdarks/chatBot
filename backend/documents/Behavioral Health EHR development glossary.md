# Behavioral Health EHR Development Glossary

*A comprehensive glossary for development teams working on behavioral health EHR integration with Claude via Amazon Bedrock*

---

## Core System Components

### **Kernel**
**Type:** System Process/Object  
A general JSON object derived from templates that describes multiple attributes of the state of person, process, or place. Acts as the central data structure for storing and processing patient information, clinical states, and system workflows.

### **Avatar**
**Type:** System Object  
Digital representation of a patient's complete clinical and behavioral profile, including all historical data, current state, and projected treatment pathways. Serves as the comprehensive patient data model.

### **Avatar Domains**
**Type:** System Object  
Categorized segments within an avatar representing different aspects of patient care (e.g., medical history, psychiatric history, social determinants, substance use, medications, treatment responses).

## Clinical Documentation

### **Progress Notes**
**Type:** Output  
Time-stamped clinical documentation capturing:
- **SOAP Notes**: Subjective, Objective, Assessment, Plan format
- **DAP Notes**: Data, Assessment, Plan format
- **BIRP Notes**: Behavior, Intervention, Response, Plan format
- **Narrative Notes**: Free-text clinical observations

Each note includes: date/time, author, discipline, interventions performed, patient response, and next steps.

### **Group Therapy Notes**
**Type:** Output  
Specialized progress notes documenting:
- Group topic and curriculum used
- Individual patient participation level
- Specific interventions for each member
- Group dynamics observations
- Individual patient responses
- Attendance record

## Clinical Processes

### **Group Therapy**
**Type:** Clinical Process  
Structured therapeutic intervention with multiple patients including:
- **Process Groups**: Focus on interpersonal dynamics
- **Psychoeducational Groups**: Skill-building and education
- **Support Groups**: Peer support and sharing
- **CBT/DBT Groups**: Evidence-based protocol groups

Includes pre-group screening, session facilitation, and post-group documentation.

### **Mental Health Rounds**
**Type:** Clinical Process  
Multidisciplinary team meeting process involving:
1. Case presentation by primary clinician
2. Review of current symptoms and behaviors
3. Medication effectiveness discussion
4. Treatment plan adjustments
5. Discharge planning updates
6. Team recommendations
7. Documentation of decisions

### **Medication Administration**
**Type:** Clinical Process  
Structured process including:
1. Medication verification (5 rights)
2. Patient identification
3. Pre-administration assessment
4. Administration documentation
5. Post-administration monitoring
6. Side effect assessment
7. Refusal documentation if applicable

## Clinical Orders and Interventions

### **Orders**
**Type:** Input/System Process  
Provider-initiated directives including:
- **Medication Orders**: Drug, dose, route, frequency, duration
- **Laboratory Orders**: Blood work, urinalysis, drug screens
- **Consultation Orders**: Specialist referrals
- **Therapeutic Orders**: Individual therapy, group therapy, activity therapy
- **Nursing Orders**: Vital signs frequency, special observations
- **Dietary Orders**: Special diets, supplements
- **Privilege Orders**: Unit restrictions, passes, discharge

### **Order Sets**
**Type:** System Object  
Pre-configured groups of orders for common scenarios (admission, detox protocols, suicide precautions).

## Clinical Observations

### **Symptoms**
**Type:** Input/Clinical Object  
Subjective experiences reported by patient including:
- **Mood Symptoms**: Depression, anxiety, euphoria, irritability
- **Psychotic Symptoms**: Hallucinations, delusions, paranoia
- **Cognitive Symptoms**: Confusion, memory problems, concentration issues
- **Behavioral Symptoms**: Agitation, withdrawal, compulsions
- **Physical Symptoms**: Sleep disturbance, appetite changes, pain

Each symptom tracked with severity, frequency, duration, and triggers.

### **Signs**
**Type:** Input/Clinical Object  
Observable, objective clinical findings including:
- **Mental Status Signs**: Appearance, behavior, speech patterns
- **Psychomotor Signs**: Agitation, retardation, tremors
- **Cognitive Signs**: Orientation, attention, memory testing results
- **Affective Signs**: Observed mood, affect congruence
- **Physiological Signs**: Vital signs, pupil response, gait
- **Side Effect Signs**: EPS, metabolic changes, sedation

### **Diagnoses**
**Type:** Output/Clinical Object  
Formal diagnostic determinations including:
- **Primary Diagnosis**: Main focus of treatment
- **Secondary Diagnoses**: Comorbid conditions
- **Rule-Out Diagnoses**: Differential considerations
- **Provisional Diagnoses**: Working diagnoses pending further assessment

Each includes:
- ICD-10 code and description
- Date of onset
- Severity specifiers
- Course specifiers
- Supporting criteria met

## Clinical Decision Support

### **cGS (Clinical Guidance System)**
**Type:** Clinical Process  
An evolved iteration of CDS that provides:
1. Real-time analysis of patient data
2. Evidence-based treatment recommendations
3. Risk stratification and alerts
4. Outcome prediction modeling
5. Treatment plan optimization
6. Medication interaction checking
7. Compliance monitoring
8. Symptom tracking and pattern recognition

### **CDS (Clinical Decision Support)**
**Type:** Clinical Process  
Traditional system providing clinicians with knowledge and patient-specific information to enhance decision-making. Includes alerts, reminders, clinical guidelines, and diagnostic support.

### **Preflighting**
**Type:** Clinical Process  
Pre-visit preparation process that:
1. Reviews previous visit notes
2. Identifies outstanding issues
3. Prepares relevant assessments
4. Flags critical changes in patient status
5. Generates preliminary agenda for visit
6. Reviews recent symptoms and signs
7. Summarizes medication responses

## Admission Process Components

### **Initial Screening**
**Type:** Clinical Process/Input  
First contact assessment determining appropriateness for admission and level of care needed.

### **Medical Clearance**
**Type:** Clinical Process  
Evaluation ensuring patient is medically stable for psychiatric treatment, including vital signs and physical examination findings.

### **Psychiatric Evaluation**
**Type:** Clinical Process  
Comprehensive assessment including:
- Chief complaint and HPI
- Systematic symptom review
- Mental status examination (documenting signs)
- Diagnosis formulation
- Initial orders

### **Psychosocial Assessment**
**Type:** Clinical Process/Input  
Detailed evaluation of social, environmental, and psychological factors affecting patient's condition.

### **Risk Assessment**
**Type:** Clinical Process  
Systematic evaluation of suicide risk, violence risk, and other safety concerns based on signs and reported symptoms.

### **Treatment Planning Meeting**
**Type:** Clinical Process  
Multidisciplinary team meeting to develop comprehensive treatment plan based on assessments, observed signs, and reported symptoms.

### **Consent and Rights Review**
**Type:** Clinical Process  
Process ensuring patient understands treatment, rights, and provides informed consent.

## Treatment Components

### **Treatment Plan**
**Type:** Output  
Comprehensive document generated from Kernel's examination of current avatar states, including:
- Problem list with associated diagnoses
- Current symptoms and signs baseline
- Gap analysis between current and target states
- SMART goals
- Interventions mapped to CPT codes
- Medication orders and monitoring plans
- Group therapy assignments
- Progress monitoring metrics
- Discharge criteria

### **SMART Goals**
**Type:** Clinical Process/Output  
Specific, Measurable, Achievable, Relevant, Time-bound objectives targeting specific symptoms and signs.

### **Discharge Summary**
**Type:** Output  
Comprehensive document summarizing:
- Admission symptoms and signs
- Hospital course and treatment response
- Final diagnoses
- Medications at discharge
- Follow-up orders
- Aftercare plans

## Medication Management

### **Medication Reconciliation**
**Type:** Clinical Process  
Systematic comparison of medication orders across transitions of care.

### **MAR (Medication Administration Record)**
**Type:** Output/System Object  
Document tracking all scheduled and PRN medications with administration times, doses, and nurse signatures.

### **Medication Education**
**Type:** Clinical Process  
Patient teaching about medications including benefits, risks, side effects to monitor.

## Administrative Processes

### **Prior Authorization**
**Type:** System Process  
Insurance approval process for services, medications, or extended treatment involving:
1. Clinical documentation submission
2. Medical necessity justification
3. Appeals process if denied
4. Tracking and follow-up

### **Billing Process**
**Type:** System Process  
Revenue cycle management including:
1. Service documentation
2. CPT code assignment
3. Claim generation
4. Submission to payers
5. Denial management
6. Payment posting

## Standards and Codes

### **CPT Codes**
**Type:** Input/System Object  
Current Procedural Terminology codes including:
- 90834: Individual psychotherapy, 45 minutes
- 90853: Group psychotherapy
- 99214: Established patient evaluation
- 90792: Psychiatric diagnostic evaluation

### **ICD-10**
**Type:** Input/System Object  
Diagnosis codes such as:
- F32.1: Major Depressive Disorder, moderate
- F41.1: Generalized Anxiety Disorder
- F20.9: Schizophrenia, unspecified

### **FHIR (Fast Healthcare Interoperability Resources)**
**Type:** System Process  
HL7 standard for exchanging healthcare information electronically, enabling interoperability between systems.

### **HIPAA Compliance**
**Type:** System Process  
Processes ensuring Protected Health Information (PHI) security including:
- Access controls
- Audit logging
- Encryption
- Business Associate Agreements
- Breach notification procedures

## AI Integration Components

### **Claude Integration Layer**
**Type:** System Process  
Interface between EHR and Claude via Amazon Bedrock for:
- Interview guidance
- Progress note generation assistance
- Symptom and sign pattern recognition
- Treatment recommendation support
- Mental health rounds preparation

### **Prompt Templates**
**Type:** Input  
Structured prompts for Claude to ensure consistent, clinically appropriate responses for:
- Progress note writing
- Symptom assessment
- Treatment planning
- Group therapy documentation

### **Response Validation**
**Type:** System Process  
Quality assurance process for AI-generated content ensuring clinical accuracy and appropriateness.

## Quality and Compliance

### **Outcome Measures**
**Type:** Output  
Standardized assessments tracking treatment effectiveness:
- PHQ-9: Depression severity
- GAD-7: Anxiety severity
- BPRS: Psychiatric symptom severity
- Clinical Global Impression scales

### **Utilization Review**
**Type:** Clinical Process  
Systematic evaluation of medical necessity, appropriateness, and efficiency of healthcare services.

### **Peer Review**
**Type:** Clinical Process  
Quality assurance process where clinicians review each other's work for adherence to standards.

### **Incident Reporting**
**Type:** System Process  
Documentation and analysis of adverse events, medication errors, or safety concerns.

---

## Usage Notes

This glossary is designed to ensure consistent understanding across development teams, particularly as development expands to India and other locations. Each entry clearly identifies whether it represents:
- **Clinical Process**: Healthcare delivery activities
- **System Process**: Technical/administrative workflows
- **Input**: Data entering the system
- **Output**: Generated documents or data
- **System Object**: Data structures or technical components
- **Clinical Object**: Clinical data elements

For Claude integration via Amazon Bedrock, focus particularly on:
1. The Kernel structure for data management
2. Avatar and Avatar Domains for patient representation
3. Clinical Decision Support components (cGS and CDS)
4. AI Integration Components for prompt design and validation

### Implementation Priority
1. **Phase 1**: Core system components (Kernel, Avatar, basic documentation)
2. **Phase 2**: Clinical processes and documentation
3. **Phase 3**: AI integration and clinical decision support
4. **Phase 4**: Administrative and compliance features

---

*Last Updated: [Current Date]*  
*Version: 1.0*  
*For: Behavioral Health EHR Development Team*