import { useEffect, useState } from 'react';
import { startTriage, answerTriage, NextTriageResponse } from '../services/triageService';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';

export function TriagePage() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [question, setQuestion] = useState<string | null>(null);
  const [assistant, setAssistant] = useState<string | null>(null);
  const [answerValue, setAnswerValue] = useState<number>(0);
  const [userText, setUserText] = useState<string>('');
  const [outcome, setOutcome] = useState<any>(null);

  useEffect(() => {
    (async () => {
      const res = await startTriage();
      setSessionId(res.session_id);
      setQuestion(res.message);
    })();
  }, []);

  async function submit() {
    if (!sessionId) return;
    const res: NextTriageResponse = await answerTriage(sessionId, Number(answerValue), userText);
    setAssistant(res.assistant_message || null);
    if (res.done) {
      setQuestion(null);
      setOutcome(res.outcome);
    } else {
      setQuestion(res.next_question || null);
      setUserText('');
      setAnswerValue(0);
    }
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-semibold mb-4">Psychological Post-Shock Triage</h1>
      <Card className="p-4 space-y-4">
        {question && (
          <div>
            <div className="mb-2 whitespace-pre-line">{question}</div>
            {assistant && <div className="text-sm text-gray-500 mb-2">{assistant}</div>}
            <div className="flex gap-2 items-center">
              <label>Answer (0-3):</label>
              <Input type="number" min={0} max={3} value={answerValue} onChange={e => setAnswerValue(Number(e.target.value))} />
            </div>
            <Input placeholder="Optional: describe how you're feeling" value={userText} onChange={e => setUserText(e.target.value)} />
            <Button className="mt-2" onClick={submit}>Next</Button>
          </div>
        )}

        {outcome && (
          <div>
            <div className="mb-2">Severity: <b>{outcome.severity.level}</b> (PHQ4 {outcome.severity.phq4_total}, GAD2 {outcome.severity.gad2_total})</div>
            <div className="mb-2">{outcome.call_to_action}</div>
            {outcome.resources?.length > 0 && (
              <ul className="list-disc pl-5">
                {outcome.resources.map((r: any, i: number) => (
                  <li key={i}>{r.name} {r.phone ? `- ${r.phone}` : ''} {r.url ? `- ${r.url}` : ''}</li>
                ))}
              </ul>
            )}
            {outcome.escalate && <div className="mt-2 text-yellow-600">A licensed counselor will be notified.</div>}
            {outcome.disclaimer && <div className="mt-4 text-xs text-gray-500 whitespace-pre-line">{outcome.disclaimer}</div>}
          </div>
        )}
      </Card>
    </div>
  );
}
