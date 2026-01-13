import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../api/auth';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../components/ui/card';

export default function VerifyEmailPage() {
    const [token, setToken] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setSuccess('');
        setLoading(true);

        try {
            await authApi.verifyEmail({ token });
            setSuccess('Email verified successfully! Redirecting to login...');
            setTimeout(() => navigate('/login'), 2000);
        } catch (err: any) {
            console.error(err);
            setError('Invalid or expired verification token.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex min-h-screen items-center justify-center bg-slate-50 p-4">
            <Card className="w-full max-w-md">
                <CardHeader>
                    <CardTitle>Verify Email</CardTitle>
                    <CardDescription>Enter the verification token sent to your email.</CardDescription>
                </CardHeader>
                <form onSubmit={handleSubmit}>
                    <CardContent className="space-y-4">
                        {error && <div className="text-sm text-red-500">{error}</div>}
                        {success && <div className="text-sm text-green-500">{success}</div>}
                        <div className="space-y-2">
                            <Label htmlFor="token">Verification Token</Label>
                            <Input
                                id="token"
                                value={token}
                                onChange={(e) => setToken(e.target.value)}
                                required
                                placeholder="Enter token here"
                                disabled={loading}
                            />
                        </div>
                    </CardContent>
                    <CardFooter>
                        <Button type="submit" className="w-full" disabled={loading}>
                            {loading ? 'Verifying...' : 'Verify Email'}
                        </Button>
                    </CardFooter>
                </form>
            </Card>
        </div>
    );
}
