import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

const AUTH_TOKEN_KEY = 'cm_auth_token';

export function getAuthToken(): string | null {
  return localStorage.getItem(AUTH_TOKEN_KEY);
}

export function setAuthToken(token: string): void {
  localStorage.setItem(AUTH_TOKEN_KEY, token);
}

export function clearAuthToken(): void {
  localStorage.removeItem(AUTH_TOKEN_KEY);
}

export interface UserResponse {
  username: string;
  email: string;
  full_name: string | null;
  proto_user_id: number;
  profile_picture: string | null;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
  user: UserResponse;
}

export function useLogin() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: {
      username: string;
      password: string;
    }): Promise<AuthResponse> => {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error('Login failed');
      return await response.json();
    },
    onSuccess: (data) => {
      queryClient.clear();
      setAuthToken(data.access_token);
    },
  });
}

export function useRegister() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: {
      username: string;
      email: string;
      password: string;
      full_name?: string;
    }): Promise<AuthResponse> => {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      if (!response.ok) throw new Error('Registration failed');
      return await response.json();
    },
    onSuccess: (data) => {
      queryClient.clear();
      setAuthToken(data.access_token);
    },
  });
}

export function useLogout() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (): Promise<{ message: string }> => {
      const token = getAuthToken();
      const response = await fetch('/api/auth/logout', {
        method: 'POST',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (!response.ok) throw new Error('Logout failed');
      return await response.json();
    },
    onSuccess: () => {
      clearAuthToken();
      queryClient.clear();
    },
  });
}

export function useCurrentUser() {
  return useQuery({
    queryKey: ['auth', 'me'],
    queryFn: async (): Promise<UserResponse> => {
      const token = getAuthToken();
      const response = await fetch('/api/auth/me', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error('Not authenticated');
      return await response.json();
    },
    enabled: !!getAuthToken(),
  });
}

export function useUpdateProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: {
      username?: string;
      email?: string;
      full_name?: string | null;
    }): Promise<UserResponse> => {
      const token = getAuthToken();
      const response = await fetch('/api/auth/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.detail || 'Failed to update profile');
      }
      return await response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['auth', 'me'] });
    },
  });
}

export function useChangePassword() {
  return useMutation({
    mutationFn: async (data: {
      current_password: string;
      new_password: string;
    }): Promise<{ message: string }> => {
      const token = getAuthToken();
      const response = await fetch('/api/auth/password', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(data),
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.detail || 'Failed to change password');
      }
      return await response.json();
    },
  });
}

export function useUploadProfilePicture() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (
      file: File,
    ): Promise<{ profile_picture_url: string }> => {
      const token = getAuthToken();
      const formData = new FormData();
      formData.append('file', file);
      const response = await fetch('/api/auth/profile/picture', {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });
      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.detail || 'Failed to upload picture');
      }
      return await response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['auth', 'me'] });
    },
  });
}
