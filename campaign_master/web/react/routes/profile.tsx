import { createFileRoute } from '@tanstack/react-router';
import { useState, useRef, useCallback } from 'react';
import {
  useCurrentUser,
  useUpdateProfile,
  useChangePassword,
  useUploadProfilePicture,
  useAuthenticatedImage,
} from '../auth';
import { UserCircleIcon, PhotoIcon } from '@heroicons/react/24/outline';

export const Route = createFileRoute('/profile')({
  component: ProfilePage,
});

function ProfilePage() {
  const { data: user, isLoading } = useCurrentUser();
  const updateProfile = useUpdateProfile();
  const changePassword = useChangePassword();
  const uploadPicture = useUploadProfilePicture();

  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [profileDirty, setProfileDirty] = useState(false);
  const [profileMsg, setProfileMsg] = useState<{
    type: 'success' | 'error';
    text: string;
  } | null>(null);

  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordMsg, setPasswordMsg] = useState<{
    type: 'success' | 'error';
    text: string;
  } | null>(null);

  const profilePicUrl = useAuthenticatedImage(user?.profile_picture);

  const [pictureMsg, setPictureMsg] = useState<{
    type: 'success' | 'error';
    text: string;
  } | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Initialize form when user data loads
  const [initialized, setInitialized] = useState(false);
  if (user && !initialized) {
    setUsername(user.username);
    setEmail(user.email);
    setFullName(user.full_name || '');
    setInitialized(true);
  }

  const handleProfileSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setProfileMsg(null);
    updateProfile.mutate(
      { username, email, full_name: fullName || null },
      {
        onSuccess: () => {
          setProfileMsg({ type: 'success', text: 'Profile updated.' });
          setProfileDirty(false);
        },
        onError: (err) => {
          setProfileMsg({ type: 'error', text: err.message });
        },
      },
    );
  };

  const handlePasswordSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPasswordMsg(null);
    if (newPassword !== confirmPassword) {
      setPasswordMsg({ type: 'error', text: 'Passwords do not match.' });
      return;
    }
    if (newPassword.length < 4) {
      setPasswordMsg({
        type: 'error',
        text: 'Password must be at least 4 characters.',
      });
      return;
    }
    changePassword.mutate(
      { current_password: currentPassword, new_password: newPassword },
      {
        onSuccess: () => {
          setPasswordMsg({ type: 'success', text: 'Password changed.' });
          setCurrentPassword('');
          setNewPassword('');
          setConfirmPassword('');
        },
        onError: (err) => {
          setPasswordMsg({ type: 'error', text: err.message });
        },
      },
    );
  };

  const handleFileUpload = useCallback(
    (file: File) => {
      setPictureMsg(null);
      const allowed = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
      if (!allowed.includes(file.type)) {
        setPictureMsg({
          type: 'error',
          text: 'Invalid file type. Use JPEG, PNG, GIF, or WebP.',
        });
        return;
      }
      if (file.size > 5 * 1024 * 1024) {
        setPictureMsg({ type: 'error', text: 'File too large. Max 5MB.' });
        return;
      }
      uploadPicture.mutate(file, {
        onSuccess: () => {
          setPictureMsg({
            type: 'success',
            text: 'Profile picture updated.',
          });
        },
        onError: (err) => {
          setPictureMsg({ type: 'error', text: err.message });
        },
      });
    },
    [uploadPicture],
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFileUpload(file);
    },
    [handleFileUpload],
  );

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[50vh] text-gray-400">
        Loading...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900">
      <div className="mx-auto max-w-3xl px-4 py-10 sm:px-6 lg:px-8">
        <h1 className="text-2xl font-semibold text-white mb-8">Your Profile</h1>

        {/* Profile Picture Section */}
        <section className="bg-gray-800 rounded-lg p-6 mb-6 border border-white/10">
          <h2 className="text-lg font-medium text-white mb-4">
            Profile Picture
          </h2>
          <div className="flex items-center gap-6">
            <div className="shrink-0">
              {profilePicUrl ? (
                <img
                  src={profilePicUrl}
                  alt="Profile"
                  className="h-20 w-20 rounded-full object-cover border-2 border-white/10"
                />
              ) : (
                <UserCircleIcon className="h-20 w-20 text-gray-500" />
              )}
            </div>
            <div
              className={`flex-1 border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
                dragOver
                  ? 'border-indigo-500 bg-indigo-500/10'
                  : 'border-gray-600 hover:border-gray-500'
              }`}
              onDragOver={(e) => {
                e.preventDefault();
                setDragOver(true);
              }}
              onDragLeave={() => setDragOver(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <PhotoIcon className="h-8 w-8 text-gray-400 mx-auto mb-2" />
              <p className="text-sm text-gray-400">
                {uploadPicture.isPending
                  ? 'Uploading...'
                  : 'Drop an image here or click to browse'}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                JPEG, PNG, GIF, WebP up to 5MB
              </p>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/png,image/gif,image/webp"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleFileUpload(file);
                  e.target.value = '';
                }}
              />
            </div>
          </div>
          {pictureMsg && (
            <p
              className={`mt-3 text-sm ${pictureMsg.type === 'success' ? 'text-green-400' : 'text-red-400'}`}
            >
              {pictureMsg.text}
            </p>
          )}
        </section>

        {/* Account Info Section */}
        <section className="bg-gray-800 rounded-lg p-6 mb-6 border border-white/10">
          <h2 className="text-lg font-medium text-white mb-4">
            Account Information
          </h2>
          <form onSubmit={handleProfileSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Username
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => {
                  setUsername(e.target.value);
                  setProfileDirty(true);
                }}
                className="w-full rounded-md bg-gray-900 border border-white/10 px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  setProfileDirty(true);
                }}
                className="w-full rounded-md bg-gray-900 border border-white/10 px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Full Name
              </label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => {
                  setFullName(e.target.value);
                  setProfileDirty(true);
                }}
                className="w-full rounded-md bg-gray-900 border border-white/10 px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            {profileMsg && (
              <p
                className={`text-sm ${profileMsg.type === 'success' ? 'text-green-400' : 'text-red-400'}`}
              >
                {profileMsg.text}
              </p>
            )}
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={updateProfile.isPending || !profileDirty}
                className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {updateProfile.isPending ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </form>
        </section>

        {/* Change Password Section */}
        <section className="bg-gray-800 rounded-lg p-6 border border-white/10">
          <h2 className="text-lg font-medium text-white mb-4">
            Change Password
          </h2>
          <form onSubmit={handlePasswordSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Current Password
              </label>
              <input
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                className="w-full rounded-md bg-gray-900 border border-white/10 px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                New Password
              </label>
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                className="w-full rounded-md bg-gray-900 border border-white/10 px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">
                Confirm New Password
              </label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full rounded-md bg-gray-900 border border-white/10 px-3 py-2 text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            {passwordMsg && (
              <p
                className={`text-sm ${passwordMsg.type === 'success' ? 'text-green-400' : 'text-red-400'}`}
              >
                {passwordMsg.text}
              </p>
            )}
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={
                  changePassword.isPending ||
                  !currentPassword ||
                  !newPassword ||
                  !confirmPassword
                }
                className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {changePassword.isPending ? 'Changing...' : 'Change Password'}
              </button>
            </div>
          </form>
        </section>
      </div>
    </div>
  );
}
