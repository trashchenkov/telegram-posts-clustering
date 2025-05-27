
import React from 'react';
import { AppTitle, IconTelegram } from '../constants';

interface HeaderProps {
  channelCount: number;
}

const Header: React.FC<HeaderProps> = ({ channelCount }) => {
  const getChannelNoun = (count: number): string => {
    const lastDigit = count % 10;
    const lastTwoDigits = count % 100;

    if (lastTwoDigits >= 11 && lastTwoDigits <= 19) {
      return 'каналов';
    }
    if (lastDigit === 1) {
      return 'канал';
    }
    if (lastDigit >= 2 && lastDigit <= 4) {
      return 'канала';
    }
    return 'каналов';
  };


  return (
    <header className="bg-slate-800 shadow-lg p-4 sticky top-0 z-50">
      <div className="container mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <span className="text-sky-400">{IconTelegram}</span>
          <h1 className="text-2xl font-bold text-sky-400">{AppTitle}</h1>
        </div>
        <div className="text-sm text-slate-400">
          Отслеживается: {channelCount} {getChannelNoun(channelCount)}
        </div>
      </div>
    </header>
  );
};

export default Header;