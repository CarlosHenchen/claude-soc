export interface User {
  id: number;
  username: string;
  full_name: string | null;
  is_admin: boolean;
  is_active: boolean;
  created_at: string;
}

export interface ScaleOption {
  value: number;
  label: string;
}
export interface Scale {
  id: number;
  key: string;
  name: string;
  min_value: number;
  max_value: number;
  options: ScaleOption[];
}
export interface Question {
  id: number;
  code: string;
  text: string;
  guidance: string | null;
  weight: number;
  order_index: number;
}
export interface Control {
  id: number;
  code: string;
  name: string;
  order_index: number;
  questions: Question[];
}
export interface Domain {
  id: number;
  key: string;
  name: string;
  reference_model: string | null;
  maintainer: string | null;
  scale_text: string | null;
  reference_url: string | null;
  order_index: number;
  scale: Scale;
  controls: Control[];
}
export interface Framework {
  id: number;
  slug: string;
  name: string;
  description: string | null;
  source_file: string | null;
}
export interface FrameworkDetail extends Framework {
  domains: Domain[];
}

export type AssessmentStatus = "draft" | "in_progress" | "completed";
export interface Assessment {
  id: number;
  framework_id: number;
  name: string;
  client: string | null;
  assessor: string | null;
  status: AssessmentStatus;
  notes: string | null;
  created_at: string;
  updated_at: string;
}
export interface ResponseItem {
  id: number;
  question_id: number;
  current_value: number | null;
  target_value: number | null;
  evidence: string | null;
  gap: number | null;
  updated_at: string;
}

export interface ScoreNode {
  scope: "overall" | "domain" | "control";
  scope_id: number | null;
  label: string | null;
  raw_score: number | null;
  normalized_pct: number | null;
  target_raw: number | null;
  target_pct: number | null;
  gap: number | null;
  scale_min: number | null;
  scale_max: number | null;
  answered: number;
  total: number;
}
export interface DomainScore extends ScoreNode {
  controls: ScoreNode[];
}
export interface Dashboard {
  assessment_id: number;
  overall: ScoreNode;
  domains: DomainScore[];
}
