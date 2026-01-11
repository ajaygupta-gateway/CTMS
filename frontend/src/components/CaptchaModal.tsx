import { useState, useEffect } from 'react';
import { Modal } from './ui/modal';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';

export default function CaptchaModal() {
    const [isOpen, setIsOpen] = useState(false);
    const [question, setQuestion] = useState('');
    const [answer, setAnswer] = useState('');

    useEffect(() => {
        const handleShowCaptcha = (event: any) => {
            setQuestion(event.detail.question);
            setIsOpen(true);
            setAnswer('');
        };

        window.addEventListener('show-captcha', handleShowCaptcha);
        return () => window.removeEventListener('show-captcha', handleShowCaptcha);
    }, []);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!answer.trim()) return;

        // Dispatch the answer
        window.dispatchEvent(new CustomEvent('captcha-solved', {
            detail: { answer: answer.trim() }
        }));
        setIsOpen(false);
    };

    return (
        <Modal
            isOpen={isOpen}
            onClose={() => {
                // If closed without solving, we notify with null
                window.dispatchEvent(new CustomEvent('captcha-solved', {
                    detail: { answer: null }
                }));
                setIsOpen(false);
            }}
            title="Security Check"
        >
            <form onSubmit={handleSubmit} className="space-y-4">
                <div className="bg-red-50 border border-red-200 p-3 rounded-md text-red-700 text-sm">
                    ⚠️ Too many failed attempts. Please solve the math problem to continue.
                </div>

                <div className="space-y-2">
                    <Label className="text-lg font-medium">What is {question}?</Label>
                    <Input
                        type="text"
                        value={answer}
                        onChange={(e) => setAnswer(e.target.value)}
                        placeholder="Enter your answer"
                        autoFocus
                        required
                    />
                </div>

                <div className="flex justify-end gap-2">
                    <Button type="submit" className="w-full">
                        Unblock My IP
                    </Button>
                </div>
            </form>
        </Modal>
    );
}
