import { apiRequest, retry } from './api';

export interface StartTriageResponse {
  session_id: string;
  message: string;
}

export async function startTriage(region?: string) {
  return retry(() => apiRequest<StartTriageResponse>('/triage/start', {
    method: 'POST',
    body: JSON.stringify({ region }),
  }));
}

export interface NextTriageResponse {
  next_question?: string;
  done: boolean;
  outcome?: any;
  assistant_message?: string;
}

export async function answerTriage(session_id: string, answer_value: number, user_text?: string) {
  return retry(() => apiRequest<NextTriageResponse>('/triage/next', {
    method: 'POST',
    body: JSON.stringify({ session_id, answer_value, user_text }),
  }));
}
