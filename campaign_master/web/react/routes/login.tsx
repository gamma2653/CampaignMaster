import { createFileRoute, useNavigate } from '@tanstack/react-router';
import { useState } from 'react';
import { useLogin, useRegister } from '../auth';
import book_closed from '../../../assets/images/icons/book2.png';

type Mode = 'login' | 'register';

const LoginComponent = () => {
  const navigate = useNavigate();
  const [mode, setMode] = useState<Mode>('login');
  const [error, setError] = useState<string | null>(null);

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');

  const loginMutation = useLogin();
  const registerMutation = useRegister();

  const isPending = loginMutation.isPending || registerMutation.isPending;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (mode === 'login') {
      loginMutation.mutate(
        { username, password },
        {
          onSuccess: () => navigate({ to: '/' }),
          onError: (err) => setError(err.message),
        },
      );
    } else {
      registerMutation.mutate(
        { username, email, password, full_name: fullName || undefined },
        {
          onSuccess: () => navigate({ to: '/' }),
          onError: (err) => setError(err.message),
        },
      );
    }
  };

  const toggleMode = () => {
    setMode(mode === 'login' ? 'register' : 'login');
    setError(null);
  };

  const inputClass =
    'w-full rounded-md border border-white/10 bg-gray-800 px-3 py-2 text-sm text-white placeholder-gray-500 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500';

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900 px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <img
            alt="Campaign Master"
            src={book_closed}
            className="h-24 w-auto mx-auto mb-4 opacity-80"
          />
          <h1 className="text-2xl font-bold text-white">Campaign Master</h1>
          <p className="text-sm text-gray-400 mt-1">
            {mode === 'login'
              ? 'Sign in to your account'
              : 'Create a new account'}
          </p>
        </div>

        <div className="rounded-lg border border-white/10 bg-gray-800/50 p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label
                htmlFor="username"
                className="block text-sm font-medium text-gray-300 mb-1"
              >
                Username
              </label>
              <input
                id="username"
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className={inputClass}
                placeholder="Enter your username"
              />
            </div>

            {mode === 'register' && (
              <>
                <div>
                  <label
                    htmlFor="email"
                    className="block text-sm font-medium text-gray-300 mb-1"
                  >
                    Email
                  </label>
                  <input
                    id="email"
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className={inputClass}
                    placeholder="you@example.com"
                  />
                </div>
                <div>
                  <label
                    htmlFor="fullName"
                    className="block text-sm font-medium text-gray-300 mb-1"
                  >
                    Full Name
                  </label>
                  <input
                    id="fullName"
                    type="text"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className={inputClass}
                    placeholder="Optional"
                  />
                </div>
              </>
            )}

            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-gray-300 mb-1"
              >
                Password
              </label>
              <input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className={inputClass}
                placeholder="Enter your password"
              />
            </div>

            {error && (
              <p className="text-sm text-red-400">{error}</p>
            )}

            <button
              type="submit"
              disabled={isPending}
              className="w-full rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-500 disabled:opacity-60 disabled:cursor-wait transition-colors"
            >
              {isPending
                ? 'Please wait...'
                : mode === 'login'
                  ? 'Log In'
                  : 'Register'}
            </button>
          </form>

          <div className="mt-4 text-center">
            <button
              type="button"
              onClick={toggleMode}
              className="text-sm text-indigo-400 hover:text-indigo-300"
            >
              {mode === 'login'
                ? "Don't have an account? Register"
                : 'Already have an account? Log in'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export const Route = createFileRoute('/login')({
  component: LoginComponent,
});
