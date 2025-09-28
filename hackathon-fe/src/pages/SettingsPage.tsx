import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { User, Lock, Bell, Moon, Sun, Shield, Save, Camera } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { useTheme } from '../contexts/ThemeContext';

const SettingsPage: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const [activeTab, setActiveTab] = useState('profile');
  const [profile, setProfile] = useState({
    firstName: 'John',
    lastName: 'Doe',
    email: 'john.doe@example.com',
    bio: 'Student passionate about learning and technology.',
    avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&h=150&fit=crop&crop=face'
  });

  const [notifications, setNotifications] = useState({
    emailNotifications: true,
    pushNotifications: false,
    weeklyReport: true,
    studyReminders: true
  });

  const [privacy, setPrivacy] = useState({
    profileVisibility: 'public',
    showProgress: true,
    shareAchievements: false
  });

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'appearance', label: 'Appearance', icon: theme === 'dark' ? Moon : Sun },
    { id: 'privacy', label: 'Privacy', icon: Shield },
    { id: 'security', label: 'Security', icon: Lock }
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: "spring" as const,
        stiffness: 300,
        damping: 24
      }
    }
  };

  const renderProfileTab = () => (
    <Card className="p-8">
      <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-6">
        Profile Information
      </h2>
      
      <div className="space-y-6">
        {/* Avatar */}
        <div className="flex items-center gap-6">
          <div className="relative">
            <img
              src={profile.avatar}
              alt="Profile"
              className="w-20 h-20 rounded-full object-cover border-4 border-white dark:border-gray-700 shadow-lg"
            />
            <button className="absolute bottom-0 right-0 p-2 bg-blue-500 text-white rounded-full shadow-lg hover:bg-blue-600 transition-colors">
              <Camera className="h-4 w-4" />
            </button>
          </div>
          <div>
            <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100">
              Profile Picture
            </h3>
            <p className="text-gray-600 dark:text-gray-400 text-sm">
              Click the camera icon to update your photo
            </p>
          </div>
        </div>

        {/* Name Fields */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              First Name
            </label>
            <Input
              value={profile.firstName}
              onChange={(e) => setProfile({...profile, firstName: e.target.value})}
              placeholder="Enter your first name"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Last Name
            </label>
            <Input
              value={profile.lastName}
              onChange={(e) => setProfile({...profile, lastName: e.target.value})}
              placeholder="Enter your last name"
            />
          </div>
        </div>

        {/* Email */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Email Address
          </label>
          <Input
            type="email"
            value={profile.email}
            onChange={(e) => setProfile({...profile, email: e.target.value})}
            placeholder="Enter your email"
          />
        </div>

        {/* Bio */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Bio
          </label>
          <textarea
            value={profile.bio}
            onChange={(e) => setProfile({...profile, bio: e.target.value})}
            placeholder="Tell us about yourself..."
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
          />
        </div>

        <Button className="w-full md:w-auto">
          <Save className="h-4 w-4 mr-2" />
          Save Changes
        </Button>
      </div>
    </Card>
  );

  const renderNotificationsTab = () => (
    <Card className="p-8">
      <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-6">
        Notification Preferences
      </h2>
      
      <div className="space-y-6">
        {[
          {
            key: 'emailNotifications',
            title: 'Email Notifications',
            description: 'Receive notifications via email'
          },
          {
            key: 'pushNotifications',
            title: 'Push Notifications',
            description: 'Receive push notifications in your browser'
          },
          {
            key: 'weeklyReport',
            title: 'Weekly Progress Report',
            description: 'Get a summary of your learning progress each week'
          },
          {
            key: 'studyReminders',
            title: 'Study Reminders',
            description: 'Reminders to help you stay on track with your studies'
          }
        ].map((item) => (
          <div key={item.key} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl">
            <div>
              <h3 className="font-medium text-gray-900 dark:text-gray-100">
                {item.title}
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {item.description}
              </p>
            </div>
            <button
              onClick={() => setNotifications({
                ...notifications,
                [item.key]: !notifications[item.key as keyof typeof notifications]
              })}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                notifications[item.key as keyof typeof notifications]
                  ? 'bg-blue-500'
                  : 'bg-gray-300 dark:bg-gray-600'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  notifications[item.key as keyof typeof notifications]
                    ? 'translate-x-6'
                    : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        ))}
      </div>
    </Card>
  );

  const renderAppearanceTab = () => (
    <Card className="p-8">
      <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-6">
        Appearance Settings
      </h2>
      
      <div className="space-y-6">
        <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium text-gray-900 dark:text-gray-100">
                Theme
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Choose between light and dark mode
              </p>
            </div>
            <Button
              onClick={toggleTheme}
              variant="outline"
              size="sm"
              className="flex items-center gap-2"
            >
              {theme === 'dark' ? (
                <>
                  <Sun className="h-4 w-4" />
                  Light
                </>
              ) : (
                <>
                  <Moon className="h-4 w-4" />
                  Dark
                </>
              )}
            </Button>
          </div>
        </div>

        <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium text-gray-900 dark:text-gray-100">
                Language
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Select your preferred language
              </p>
            </div>
            <select className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100">
              <option value="en">English</option>
              <option value="es">Spanish</option>
              <option value="fr">French</option>
              <option value="de">German</option>
            </select>
          </div>
        </div>

        <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium text-gray-900 dark:text-gray-100">
                Timezone
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Your local timezone for scheduling
              </p>
            </div>
            <select className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100">
              <option value="UTC-8">Pacific Time (UTC-8)</option>
              <option value="UTC-5">Eastern Time (UTC-5)</option>
              <option value="UTC+0">Greenwich Mean Time (UTC+0)</option>
              <option value="UTC+1">Central European Time (UTC+1)</option>
            </select>
          </div>
        </div>
      </div>
    </Card>
  );

  const renderPrivacyTab = () => (
    <Card className="p-8">
      <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-6">
        Privacy Settings
      </h2>
      
      <div className="space-y-6">
        <div className="p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-medium text-gray-900 dark:text-gray-100">
                Profile Visibility
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Control who can see your profile
              </p>
            </div>
            <select 
              value={privacy.profileVisibility}
              onChange={(e) => setPrivacy({...privacy, profileVisibility: e.target.value})}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
            >
              <option value="public">Public</option>
              <option value="friends">Friends Only</option>
              <option value="private">Private</option>
            </select>
          </div>
        </div>

        {[
          {
            key: 'showProgress',
            title: 'Show Learning Progress',
            description: 'Allow others to see your learning progress and achievements'
          },
          {
            key: 'shareAchievements',
            title: 'Share Achievements',
            description: 'Automatically share your achievements with friends'
          }
        ].map((item) => (
          <div key={item.key} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800/50 rounded-xl">
            <div>
              <h3 className="font-medium text-gray-900 dark:text-gray-100">
                {item.title}
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                {item.description}
              </p>
            </div>
            <button
              onClick={() => setPrivacy({
                ...privacy,
                [item.key]: !privacy[item.key as keyof typeof privacy]
              })}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                privacy[item.key as keyof typeof privacy]
                  ? 'bg-blue-500'
                  : 'bg-gray-300 dark:bg-gray-600'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  privacy[item.key as keyof typeof privacy]
                    ? 'translate-x-6'
                    : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        ))}
      </div>
    </Card>
  );

  const renderSecurityTab = () => (
    <Card className="p-8">
      <h2 className="text-2xl font-semibold text-gray-900 dark:text-gray-100 mb-6">
        Security Settings
      </h2>
      
      <div className="space-y-6">
        <div className="p-6 bg-gradient-to-r from-red-50 to-red-100 dark:from-red-950/20 dark:to-red-900/20 rounded-xl border border-red-200 dark:border-red-800">
          <h3 className="font-medium text-red-800 dark:text-red-300 mb-2">
            Change Password
          </h3>
          <p className="text-red-600 dark:text-red-400 text-sm mb-4">
            Update your password to keep your account secure
          </p>
          <div className="space-y-4">
            <Input type="password" placeholder="Current password" />
            <Input type="password" placeholder="New password" />
            <Input type="password" placeholder="Confirm new password" />
            <Button variant="outline" className="border-red-300 text-red-700 hover:bg-red-50 dark:border-red-700 dark:text-red-300 dark:hover:bg-red-950/20">
              Update Password
            </Button>
          </div>
        </div>

        {/* Two-Factor Authentication and Active Sessions have been removed per request */}
      </div>
    </Card>
  );

  const renderTabContent = () => {
    switch (activeTab) {
      case 'profile': return renderProfileTab();
      case 'notifications': return renderNotificationsTab();
      case 'appearance': return renderAppearanceTab();
      case 'privacy': return renderPrivacyTab();
      case 'security': return renderSecurityTab();
      default: return renderProfileTab();
    }
  };

  return (
    <motion.div
      className="space-y-8"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <motion.div variants={itemVariants}>
        <h1 className="text-4xl font-bold bg-gradient-to-r from-orange-600 to-red-600 bg-clip-text text-transparent">
          Settings
        </h1>
        <p className="text-gray-600 dark:text-gray-400 mt-2">
          Manage your account preferences and settings
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Sidebar */}
        <motion.div variants={itemVariants} className="lg:col-span-1">
          <Card className="p-4">
            <nav className="space-y-2">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center gap-3 px-4 py-3 text-left rounded-xl transition-colors ${
                      activeTab === tab.id
                        ? 'bg-blue-50 dark:bg-blue-950/20 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-800'
                        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800/50'
                    }`}
                  >
                    <Icon className="h-5 w-5" />
                    <span className="font-medium">{tab.label}</span>
                  </button>
                );
              })}
            </nav>
          </Card>
        </motion.div>

        {/* Main Content */}
        <motion.div variants={itemVariants} className="lg:col-span-3">
          {renderTabContent()}
        </motion.div>
      </div>
    </motion.div>
  );
};

export default SettingsPage;