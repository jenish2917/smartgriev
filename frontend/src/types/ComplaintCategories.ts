/**
 * Comprehensive Complaint Classification System
 * Categories, subcategories, and components for Indian Government Services
 */

export interface ComplaintCategory {
  id: string;
  name: string;
  description: string;
  icon: string;
  color: string;
  subcategories: ComplaintSubcategory[];
  priority: 'low' | 'medium' | 'high' | 'urgent';
  estimatedResolutionTime: string;
  responsibleDepartment: string;
}

export interface ComplaintSubcategory {
  id: string;
  name: string;
  description: string;
  icon: string;
  components: ComplaintComponent[];
  requiresLocation: boolean;
  requiresEvidence: boolean;
  commonIssues: string[];
}

export interface ComplaintComponent {
  id: string;
  name: string;
  description: string;
  icon: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  examples: string[];
  requiredFields: string[];
  optionalFields: string[];
}

export const COMPLAINT_CATEGORIES: ComplaintCategory[] = [
  {
    id: 'infrastructure',
    name: 'Infrastructure & Public Works',
    description: 'Roads, bridges, buildings, and public infrastructure issues',
    icon: '🏗️',
    color: '#FF9933',
    priority: 'high',
    estimatedResolutionTime: '7-15 days',
    responsibleDepartment: 'Public Works Department',
    subcategories: [
      {
        id: 'roads-transport',
        name: 'Roads & Transportation',
        description: 'Road conditions, traffic, and transport infrastructure',
        icon: '🛣️',
        requiresLocation: true,
        requiresEvidence: true,
        commonIssues: ['Potholes', 'Traffic signals', 'Road maintenance', 'Street lighting'],
        components: [
          {
            id: 'potholes',
            name: 'Potholes & Road Damage',
            description: 'Damaged roads, potholes, broken pavements',
            icon: '🕳️',
            severity: 'high',
            examples: ['Large potholes on main road', 'Broken pavement near school', 'Road surface deterioration'],
            requiredFields: ['location', 'description', 'photo'],
            optionalFields: ['traffic_impact', 'safety_concern']
          },
          {
            id: 'street-lights',
            name: 'Street Lighting',
            description: 'Non-functional or damaged street lights',
            icon: '💡',
            severity: 'medium',
            examples: ['Street light not working', 'Broken lamp post', 'Dark streets at night'],
            requiredFields: ['location', 'description'],
            optionalFields: ['photo', 'safety_impact']
          },
          {
            id: 'traffic-signals',
            name: 'Traffic Signals & Signs',
            description: 'Faulty traffic lights, missing road signs',
            icon: '🚦',
            severity: 'critical',
            examples: ['Traffic light not working', 'Missing stop sign', 'Broken traffic signal'],
            requiredFields: ['location', 'description', 'urgency'],
            optionalFields: ['photo', 'alternative_route']
          }
        ]
      },
      {
        id: 'public-buildings',
        name: 'Public Buildings & Facilities',
        description: 'Government buildings, parks, and public facilities',
        icon: '🏛️',
        requiresLocation: true,
        requiresEvidence: false,
        commonIssues: ['Building maintenance', 'Accessibility issues', 'Facility cleanliness'],
        components: [
          {
            id: 'building-maintenance',
            name: 'Building Maintenance',
            description: 'Structural issues, repairs needed in public buildings',
            icon: '🔧',
            severity: 'medium',
            examples: ['Leaking roof in government office', 'Broken windows', 'Paint peeling'],
            requiredFields: ['building_name', 'location', 'description'],
            optionalFields: ['photo', 'affected_services']
          },
          {
            id: 'accessibility',
            name: 'Accessibility Issues',
            description: 'Lack of disabled access, ramps, elevators',
            icon: '♿',
            severity: 'high',
            examples: ['No wheelchair ramp', 'Broken elevator', 'Inaccessible restrooms'],
            requiredFields: ['building_name', 'location', 'accessibility_type'],
            optionalFields: ['photo', 'suggested_solution']
          }
        ]
      }
    ]
  },
  {
    id: 'utilities',
    name: 'Utilities & Essential Services',
    description: 'Water, electricity, gas, waste management, and sewage services',
    icon: '⚡',
    color: '#138808',
    priority: 'urgent',
    estimatedResolutionTime: '1-7 days',
    responsibleDepartment: 'Municipal Corporation',
    subcategories: [
      {
        id: 'electricity',
        name: 'Electricity Supply',
        description: 'Power outages, electrical faults, billing issues',
        icon: '💡',
        requiresLocation: true,
        requiresEvidence: false,
        commonIssues: ['Power outage', 'Voltage fluctuation', 'Billing disputes', 'Meter issues'],
        components: [
          {
            id: 'power-outage',
            name: 'Power Outage',
            description: 'No electricity supply in area',
            icon: '🔌',
            severity: 'critical',
            examples: ['No power for 3 days', 'Frequent power cuts', 'Transformer failure'],
            requiredFields: ['location', 'duration', 'affected_area'],
            optionalFields: ['previous_complaints', 'alternative_power']
          },
          {
            id: 'voltage-issues',
            name: 'Voltage Problems',
            description: 'Low voltage, fluctuations, electrical safety issues',
            icon: '⚡',
            severity: 'high',
            examples: ['Low voltage affecting appliances', 'Power fluctuations', 'Burnt appliances due to voltage'],
            requiredFields: ['location', 'description', 'impact'],
            optionalFields: ['meter_reading', 'appliance_damage']
          }
        ]
      },
      {
        id: 'water-supply',
        name: 'Water Supply',
        description: 'Water shortage, quality issues, pipeline problems',
        icon: '💧',
        requiresLocation: true,
        requiresEvidence: true,
        commonIssues: ['No water supply', 'Poor water quality', 'Pipeline leakage', 'Low pressure'],
        components: [
          {
            id: 'water-shortage',
            name: 'Water Shortage',
            description: 'Insufficient or no water supply',
            icon: '🚰',
            severity: 'critical',
            examples: ['No water for a week', 'Very low water pressure', 'Irregular water supply'],
            requiredFields: ['location', 'duration', 'affected_households'],
            optionalFields: ['alternative_source', 'tank_capacity']
          },
          {
            id: 'water-quality',
            name: 'Water Quality Issues',
            description: 'Contaminated, dirty, or undrinkable water',
            icon: '🧪',
            severity: 'critical',
            examples: ['Dirty water from tap', 'Bad smell in water', 'Health issues from water'],
            requiredFields: ['location', 'description', 'water_sample'],
            optionalFields: ['photo', 'health_impact', 'lab_test']
          }
        ]
      },
      {
        id: 'waste-management',
        name: 'Waste Management',
        description: 'Garbage collection, sewage, sanitation issues',
        icon: '🗑️',
        requiresLocation: true,
        requiresEvidence: true,
        commonIssues: ['Garbage not collected', 'Overflowing bins', 'Sewage overflow', 'Illegal dumping'],
        components: [
          {
            id: 'garbage-collection',
            name: 'Garbage Collection',
            description: 'Issues with waste pickup and disposal',
            icon: '🚛',
            severity: 'medium',
            examples: ['Garbage not collected for days', 'Overflowing dustbins', 'Irregular collection schedule'],
            requiredFields: ['location', 'last_collection_date', 'waste_type'],
            optionalFields: ['photo', 'health_hazard', 'odor_issue']
          },
          {
            id: 'sewage-overflow',
            name: 'Sewage & Drainage',
            description: 'Blocked drains, sewage overflow, flooding',
            icon: '🌊',
            severity: 'critical',
            examples: ['Sewage overflowing on street', 'Blocked storm drain', 'Flooding during rain'],
            requiredFields: ['location', 'description', 'urgency'],
            optionalFields: ['photo', 'water_logging', 'health_risk']
          }
        ]
      }
    ]
  },
  {
    id: 'healthcare',
    name: 'Healthcare & Medical Services',
    description: 'Hospitals, clinics, medical facilities, and health services',
    icon: '🏥',
    color: '#000080',
    priority: 'urgent',
    estimatedResolutionTime: '1-3 days',
    responsibleDepartment: 'Health Department',
    subcategories: [
      {
        id: 'hospital-services',
        name: 'Hospital & Clinic Services',
        description: 'Healthcare facility issues and service quality',
        icon: '🩺',
        requiresLocation: true,
        requiresEvidence: false,
        commonIssues: ['Staff behavior', 'Equipment failure', 'Cleanliness', 'Long waiting times'],
        components: [
          {
            id: 'staff-behavior',
            name: 'Staff Behavior & Service',
            description: 'Unprofessional behavior, negligence, poor service',
            icon: '👨‍⚕️',
            severity: 'high',
            examples: ['Rude doctor behavior', 'Nurse negligence', 'Delayed treatment'],
            requiredFields: ['hospital_name', 'staff_name', 'incident_description'],
            optionalFields: ['date_time', 'witness', 'previous_complaints']
          },
          {
            id: 'medical-equipment',
            name: 'Medical Equipment Issues',
            description: 'Broken or non-functional medical equipment',
            icon: '🔬',
            severity: 'critical',
            examples: ['X-ray machine not working', 'Broken ventilator', 'No oxygen supply'],
            requiredFields: ['hospital_name', 'equipment_type', 'impact'],
            optionalFields: ['alternative_available', 'patient_affected']
          }
        ]
      }
    ]
  },
  {
    id: 'education',
    name: 'Education & Schools',
    description: 'Schools, colleges, educational policies, and student facilities',
    icon: '🎓',
    color: '#FF6B35',
    priority: 'medium',
    estimatedResolutionTime: '5-10 days',
    responsibleDepartment: 'Education Department',
    subcategories: [
      {
        id: 'school-infrastructure',
        name: 'School Infrastructure',
        description: 'Building conditions, facilities, and safety in schools',
        icon: '🏫',
        requiresLocation: true,
        requiresEvidence: true,
        commonIssues: ['Building repairs', 'Toilet facilities', 'Playground safety', 'Classroom conditions'],
        components: [
          {
            id: 'building-safety',
            name: 'Building Safety & Maintenance',
            description: 'Structural issues, safety hazards in school buildings',
            icon: '⚠️',
            severity: 'high',
            examples: ['Cracked walls in classroom', 'Leaking roof', 'Unsafe playground equipment'],
            requiredFields: ['school_name', 'location', 'safety_issue'],
            optionalFields: ['photo', 'students_affected', 'immediate_danger']
          }
        ]
      }
    ]
  },
  {
    id: 'social-services',
    name: 'Social Services & Welfare',
    description: 'Pension, welfare schemes, social security, and citizen services',
    icon: '🤝',
    color: '#8E44AD',
    priority: 'medium',
    estimatedResolutionTime: '10-20 days',
    responsibleDepartment: 'Social Welfare Department',
    subcategories: [
      {
        id: 'pension-welfare',
        name: 'Pension & Welfare Schemes',
        description: 'Issues with government pension and welfare schemes',
        icon: '💰',
        requiresLocation: false,
        requiresEvidence: true,
        commonIssues: ['Delayed pension', 'Application rejected', 'Document issues', 'Benefit not received'],
        components: [
          {
            id: 'pension-delay',
            name: 'Pension Payment Delay',
            description: 'Delayed or missing pension payments',
            icon: '📅',
            severity: 'high',
            examples: ['Pension not received for 3 months', 'Wrong amount credited', 'Account not updated'],
            requiredFields: ['pension_type', 'application_number', 'last_payment_date'],
            optionalFields: ['bank_details', 'previous_complaints', 'financial_hardship']
          }
        ]
      }
    ]
  }
];

export const URGENCY_LEVELS = [
  { id: 'low', name: 'Low', description: 'Can wait for normal processing', color: '#52C41A', icon: '🟢' },
  { id: 'medium', name: 'Medium', description: 'Should be addressed soon', color: '#FA8C16', icon: '🟡' },
  { id: 'high', name: 'High', description: 'Requires prompt attention', color: '#FF4D4F', icon: '🟠' },
  { id: 'urgent', name: 'Urgent', description: 'Immediate action required', color: '#A0202C', icon: '🔴' }
];

export const EVIDENCE_TYPES = [
  { id: 'photo', name: 'Photograph', icon: '📷', description: 'Visual evidence of the issue' },
  { id: 'document', name: 'Document', icon: '📄', description: 'Bills, receipts, official papers' },
  { id: 'audio', name: 'Audio Recording', icon: '🎵', description: 'Audio evidence or voice note' },
  { id: 'witness', name: 'Witness Statement', icon: '👥', description: 'Contact details of witnesses' }
];