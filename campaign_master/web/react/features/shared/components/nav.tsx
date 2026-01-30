// From https://tailwindcss.com/plus/ui-blocks/application-ui/navigation/navbars

// import React from 'react'
import {
  Disclosure,
  DisclosureButton,
  DisclosurePanel,
  Menu,
  MenuButton,
  MenuItem,
  MenuItems,
  Switch,
} from '@headlessui/react';
import {
  Bars3Icon,
  BellIcon,
  XMarkIcon,
  Cog6ToothIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline';
import { Link, useNavigate } from '@tanstack/react-router';
import book_closed from '../../../../../assets/images/icons/book2.png';
import me from '../../../../../assets/images/Me.jpg';
import { useCreateCampaignPlan } from '../../../query';
import { useRouter } from '@tanstack/react-router';
import { useAI } from '../../ai/AIContext';
import {
  useLogout,
  useCurrentUser,
  clearAuthToken,
  useAuthenticatedImage,
} from '../../../auth';
import { UserCircleIcon } from '@heroicons/react/24/outline';

const navigation = [
  { name: 'My Campaign Plans', href: '/campaign/plans', current: true },
] as const;

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ');
}

export default function Navbar() {
  const navigate = useNavigate();
  const router = useRouter();
  const createMutation = useCreateCampaignPlan();
  const { enabled: aiEnabled, setEnabled: setAIEnabled } = useAI();
  const logoutMutation = useLogout();
  const { data: currentUser } = useCurrentUser();
  const profilePicUrl = useAuthenticatedImage(currentUser?.profile_picture);

  const handleSignOut = () => {
    logoutMutation.mutate(undefined, {
      onSuccess: () => navigate({ to: '/login' }),
      onError: () => {
        clearAuthToken();
        navigate({ to: '/login' });
      },
    });
  };

  const handleCreateNew = async () => {
    createMutation.mutate(
      {
        title: 'New Campaign',
        version: '0.0.1',
        setting: '',
        summary: '',
        storyline: [],
        storypoints: [],
        characters: [],
        locations: [],
        items: [],
        rules: [],
        objectives: [],
      },
      {
        onSuccess: (newCampaign) => {
          navigate({ to: `/campaign/plan/${newCampaign.obj_id.numeric}` });
        },
        onError: (error) => {
          alert(`Failed to create campaign: ${error.message}`);
          router.invalidate();
        },
      },
    );
  };

  return (
    <Disclosure
      as="nav"
      className="relative bg-gray-800/50 after:pointer-events-none after:absolute after:inset-x-0 after:bottom-0 after:h-px after:bg-white/10"
    >
      <div className="mx-auto max-w-7xl px-2 sm:px-6 lg:px-8">
        <div className="relative flex h-16 items-center justify-between">
          <div className="absolute inset-y-0 left-0 flex items-center sm:hidden">
            {/* Mobile menu button*/}
            <DisclosureButton className="group relative inline-flex items-center justify-center rounded-md p-2 text-gray-400 hover:bg-white/5 hover:text-white focus:outline-2 focus:-outline-offset-1 focus:outline-indigo-500">
              <span className="absolute -inset-0.5" />
              <span className="sr-only">Open main menu</span>
              <Bars3Icon
                aria-hidden="true"
                className="block size-6 group-data-open:hidden"
              />
              <XMarkIcon
                aria-hidden="true"
                className="hidden size-6 group-data-open:block"
              />
            </DisclosureButton>
          </div>
          <div className="flex flex-1 items-center justify-center sm:items-stretch sm:justify-start">
            <div className="flex shrink-0 items-center">
              <Link to="/">
                <img
                  alt="Campaign Master"
                  src={book_closed}
                  className="h-8 w-auto"
                />
              </Link>
            </div>
            <div className="hidden sm:ml-6 sm:block">
              <div className="flex space-x-4">
                {navigation.map((item) => (
                  <a
                    key={item.name}
                    href={item.href}
                    aria-current={item.current ? 'page' : undefined}
                    className={classNames(
                      item.current
                        ? 'bg-gray-950/50 text-white'
                        : 'text-gray-300 hover:bg-white/5 hover:text-white',
                      'rounded-md px-3 py-2 text-sm font-medium',
                    )}
                  >
                    {item.name}
                  </a>
                ))}
                <button
                  onClick={handleCreateNew}
                  disabled={createMutation.isPending}
                  className="text-gray-300 hover:bg-white/5 hover:text-white disabled:cursor-wait rounded-md px-3 py-2 text-sm font-medium"
                >
                  {createMutation.isPending ? 'Creating...' : 'New Campaign'}
                </button>
              </div>
            </div>
          </div>
          <div className="absolute inset-y-0 right-0 flex items-center pr-2 sm:static sm:inset-auto sm:ml-6 sm:pr-0">
            <button
              type="button"
              className="relative rounded-full p-1 text-gray-400 hover:text-white focus:outline-2 focus:outline-offset-2 focus:outline-indigo-500"
            >
              <span className="absolute -inset-1.5" />
              <span className="sr-only">View notifications</span>
              <BellIcon aria-hidden="true" className="size-6" />
            </button>

            {/* Profile dropdown */}
            <Menu as="div" className="relative ml-3">
              <MenuButton className="relative flex rounded-full focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500">
                <span className="absolute -inset-1.5" />
                <span className="sr-only">Open user menu</span>
                {profilePicUrl ? (
                  <img
                    alt=""
                    src={profilePicUrl}
                    className="size-8 rounded-full bg-gray-800 object-cover outline -outline-offset-1 outline-white/10"
                  />
                ) : (
                  <img
                    alt=""
                    src={me}
                    className="size-8 rounded-full bg-gray-800 outline -outline-offset-1 outline-white/10"
                  />
                )}
              </MenuButton>

              <MenuItems
                transition
                className="absolute right-0 z-10 mt-2 w-56 origin-top-right rounded-md bg-gray-800 py-1 outline -outline-offset-1 outline-white/10 transition data-closed:scale-95 data-closed:transform data-closed:opacity-0 data-enter:duration-100 data-enter:ease-out data-leave:duration-75 data-leave:ease-in"
              >
                <MenuItem>
                  <Link
                    to="/profile"
                    className="block px-4 py-2 text-sm text-gray-300 data-focus:bg-white/5 data-focus:outline-hidden"
                  >
                    Your profile
                  </Link>
                </MenuItem>
                <MenuItem>
                  <Link
                    to="/settings/agents"
                    className="flex items-center gap-2 px-4 py-2 text-sm text-gray-300 data-focus:bg-white/5 data-focus:outline-hidden"
                  >
                    <SparklesIcon className="h-4 w-4" />
                    AI Settings
                  </Link>
                </MenuItem>
                <MenuItem>
                  <div
                    className="flex items-center justify-between px-4 py-2 text-sm text-gray-300 data-focus:bg-white/5 data-focus:outline-hidden cursor-pointer"
                    onClick={(e) => {
                      e.preventDefault();
                      setAIEnabled(!aiEnabled);
                    }}
                  >
                    <span className="flex items-center gap-2">
                      <Cog6ToothIcon className="h-4 w-4" />
                      Enable AI
                    </span>
                    <Switch
                      checked={aiEnabled}
                      onChange={setAIEnabled}
                      className={`${
                        aiEnabled ? 'bg-blue-600' : 'bg-gray-600'
                      } relative inline-flex h-5 w-9 items-center rounded-full transition-colors`}
                    >
                      <span
                        className={`${
                          aiEnabled ? 'translate-x-5' : 'translate-x-1'
                        } inline-block h-3 w-3 transform rounded-full bg-white transition-transform`}
                      />
                    </Switch>
                  </div>
                </MenuItem>
                <div className="border-t border-gray-700 my-1" />
                <MenuItem>
                  <button
                    onClick={handleSignOut}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-300 data-focus:bg-white/5 data-focus:outline-hidden"
                  >
                    Sign out
                  </button>
                </MenuItem>
              </MenuItems>
            </Menu>
          </div>
        </div>
      </div>

      <DisclosurePanel className="sm:hidden">
        <div className="space-y-1 px-2 pt-2 pb-3">
          {navigation.map((item) => (
            <Link to={item.href}>
              <DisclosureButton
                key={item.name}
                as="div"
                aria-current={item.current ? 'page' : undefined}
                className={classNames(
                  item.current
                    ? 'bg-gray-950/50 text-white'
                    : 'text-gray-300 hover:bg-white/5 hover:text-white',
                  'block rounded-md px-3 py-2 text-base font-medium',
                )}
              >
                {item.name}
              </DisclosureButton>
            </Link>
          ))}
          <DisclosureButton
            as="button"
            onClick={handleCreateNew}
            disabled={createMutation.isPending}
            className="text-gray-300 hover:bg-white/5 hover:text-white disabled:cursor-wait block rounded-md px-3 py-2 text-base font-medium w-full text-left"
          >
            {createMutation.isPending ? 'Creating...' : 'New Campaign'}
          </DisclosureButton>
        </div>
      </DisclosurePanel>
    </Disclosure>
  );
}
