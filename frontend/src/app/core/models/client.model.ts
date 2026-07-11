export interface Client {
  id: number;
  agent_code: string;
  from_date : string;
  to_date : string;
  policy_holder: string;
  email: string | null;
  phone_number: string;
  address: string;
  mode: string;
  dob: string;
  family_code: string;
  policy_number: string;
  agency_code: string;
  commecement_date: string;
  plan: number;
  term: number;
  ppt: number;
  sum_assured: number;
  premium: number;
  fup_date: string;
  nominee: string;
}

export type NewClient = Omit<Client, 'id'>;