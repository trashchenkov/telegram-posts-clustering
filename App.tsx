import React, { useState, useCallback, useEffect, useMemo } from 'react';
import { Post, ChannelUsername } from './types';
import { DEFAULT_CHANNELS, IconDownload, IconRefresh } from './constants';
import Header from './components/Header';
import PostCard from './components/PostCard';
import LoadingSpinner from './components/LoadingSpinner';
import { fetchRecentPosts } from './services/postService';
import { downloadJson } from './utils/fileUtils';

const App: React.FC = () => {
  const [posts, setPosts] = useState<Post[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [monitoredChannels, setMonitoredChannels] = useState<ChannelUsername[]>(DEFAULT_CHANNELS);
  const [expandedClusters, setExpandedClusters] = useState<Set<string>>(new Set());

  const getPostNoun = (count: number): string => {
    const lastDigit = count % 10;
    const lastTwoDigits = count % 100;

    if (lastTwoDigits >= 11 && lastTwoDigits <= 19) {
      return 'постов';
    }
    if (lastDigit === 1) {
      return 'пост';
    }
    if (lastDigit >= 2 && lastDigit <= 4) {
      return 'поста';
    }
    return 'постов';
  };

  const loadAndClusterPosts = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    setPosts([]); // Clear previous posts
    setExpandedClusters(new Set()); // Collapse all clusters on new load
    try {
      // Backend now returns already clustered posts
      const clusteredPosts = await fetchRecentPosts(monitoredChannels);
      if (clusteredPosts.length === 0) {
        setError("За последние 24 часа по указанным каналам посты не найдены.");
        return;
      }
      setPosts(clusteredPosts);
    } catch (err) {
      console.error("Ошибка при загрузке постов:", err);
      setError("Не удалось загрузить посты. Пожалуйста, попробуйте еще раз.");
      setPosts([]);
    } finally {
      setIsLoading(false);
    }
  }, [monitoredChannels]);

  useEffect(() => {
    // For this example, we'll require a button click to load.
  }, []);

  const handleFetchClick = () => {
    loadAndClusterPosts();
  };

  const handleDownloadJson = () => {
    if (posts.length > 0) {
      downloadJson(posts, 'telegram_posts.json');
    }
  };

  const toggleClusterExpansion = (clusterName: string) => {
    setExpandedClusters((prevExpanded: Set<string>) => {
      const newExpanded = new Set(prevExpanded);
      if (newExpanded.has(clusterName)) {
        newExpanded.delete(clusterName);
      } else {
        newExpanded.add(clusterName);
      }
      return newExpanded;
    });
  };

  const groupedPosts = useMemo(() => {
    if (!posts.length) return [];
    const groups = posts.reduce((acc: Record<string, Post[]>, post: Post) => {
      const cluster = post.clusterName || 'Некатегоризованные';
      if (!acc[cluster]) {
        acc[cluster] = [];
      }
      acc[cluster].push(post);
      return acc;
    }, {} as Record<string, Post[]>);

    return Object.entries(groups).sort(([clusterA], [clusterB]) =>
      clusterA.localeCompare(clusterB)
    );
  }, [posts]);


  return (
    <div className="min-h-screen flex flex-col">
      <Header channelCount={monitoredChannels.length} />
      
      <main className="container mx-auto p-4 sm:p-6 lg:p-8 flex-grow">
        <div className="bg-slate-800 shadow-md rounded-lg p-6 mb-8">
          <h2 className="text-xl font-semibold text-sky-300 mb-3">Отслеживаемые каналы</h2>
          <p className="text-slate-400 mb-4 text-sm">
            Приложение в настоящее время отслеживает следующие Telegram-каналы на предмет постов, опубликованных за последние 24 часа. 
            Кластеризация выполняется с использованием машинного обучения и LLM для создания умных названий кластеров.
          </p>
          <div className="bg-slate-700 p-3 rounded">
            <p className="text-slate-300 font-mono text-sm whitespace-pre-wrap">
              {monitoredChannels.join(',\n')}
            </p>
          </div>
          <div className="mt-6 flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-4">
            <button
              onClick={handleFetchClick}
              disabled={isLoading}
              className="flex-1 w-full sm:w-auto bg-sky-600 hover:bg-sky-500 disabled:bg-sky-800 disabled:text-slate-400 text-white font-semibold py-3 px-6 rounded-lg shadow-md hover:shadow-lg transition duration-150 ease-in-out flex items-center justify-center space-x-2"
              aria-label="Загрузить и кластеризовать посты"
            >
              {IconRefresh}
              <span>{isLoading ? 'Загрузка...' : 'Загрузить и кластеризовать посты'}</span>
            </button>
            {posts.length > 0 && !isLoading && (
              <button
                onClick={handleDownloadJson}
                className="flex-1 w-full sm:w-auto bg-green-600 hover:bg-green-500 text-white font-semibold py-3 px-6 rounded-lg shadow-md hover:shadow-lg transition duration-150 ease-in-out flex items-center justify-center space-x-2"
                aria-label="Скачать JSON"
              >
                {IconDownload}
                <span>Скачать JSON</span>
              </button>
            )}
          </div>
        </div>

        {isLoading && <LoadingSpinner />}
        
        {error && !isLoading && (
          <div className="bg-red-700/50 border border-red-700 text-red-200 px-4 py-3 rounded-lg relative mb-6" role="alert">
            <strong className="font-bold">Ошибка: </strong>
            <span className="block sm:inline">{error}</span>
          </div>
        )}

        {!isLoading && !error && posts.length === 0 && (
           <div className="text-center py-10 text-slate-400">
             <p className="text-lg">Нет постов для отображения.</p>
             <p>Нажмите "Загрузить и кластеризовать посты", чтобы загрузить данные.</p>
           </div>
        )}

        {!isLoading && posts.length > 0 && (
          <div className="space-y-6">
            {groupedPosts.map(([clusterName, postsInCluster]: [string, Post[]]) => (
              <div key={clusterName} className="bg-slate-800 shadow-lg rounded-lg overflow-hidden">
                <button
                  onClick={() => toggleClusterExpansion(clusterName)}
                  className="w-full flex justify-between items-center text-left p-4 bg-slate-700 hover:bg-slate-600/70 transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-sky-500"
                  aria-expanded={expandedClusters.has(clusterName)}
                  aria-controls={`cluster-content-${clusterName.replace(/\s+/g, '-')}`}
                >
                  <h3 className="text-lg sm:text-xl font-semibold text-sky-300">
                    {clusterName} 
                    <span className="text-sm font-normal text-slate-400 ml-2">
                      ({postsInCluster.length} {getPostNoun(postsInCluster.length)})
                    </span>
                  </h3>
                  <svg 
                    xmlns="http://www.w3.org/2000/svg" 
                    fill="none" 
                    viewBox="0 0 24 24" 
                    strokeWidth={2} 
                    stroke="currentColor" 
                    className={`w-5 h-5 sm:w-6 sm:h-6 text-slate-400 transform transition-transform duration-200 ${expandedClusters.has(clusterName) ? 'rotate-180' : 'rotate-0'}`}
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 8.25l-7.5 7.5-7.5-7.5" />
                  </svg>
                </button>
                {expandedClusters.has(clusterName) && (
                  <div 
                    id={`cluster-content-${clusterName.replace(/\s+/g, '-')}`}
                    className="p-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
                  >
                    {postsInCluster.map((post: Post) => (
                      <PostCard key={post.id} post={post} />
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </main>

      <footer className="bg-slate-800 text-center p-4 text-sm text-slate-500 border-t border-slate-700">
        Агрегатор постов Telegram &copy; {new Date().getFullYear()}
      </footer>
    </div>
  );
};

export default App;
