
import React from 'react';
import { Post } from '../types';
import { IconLightBulb } from '../constants';

interface PostCardProps {
  post: Post;
}

const PostCard: React.FC<PostCardProps> = ({ post }) => {
  const { channelName, publicationDateTime, postLink, postText, hasMedia, clusterName } = post;

  const formattedDate = new Date(publicationDateTime).toLocaleString('ru-RU'); // Используем локаль ru-RU

  return (
    <div className="bg-slate-800 shadow-lg rounded-lg p-6 mb-6 hover:shadow-sky-500/30 transition-shadow duration-300">
      <div className="flex justify-between items-start mb-3">
        <div>
          <h3 className="text-xl font-semibold text-sky-400">{channelName}</h3>
          <p className="text-xs text-slate-400">{formattedDate}</p>
        </div>
        {clusterName && (
          <div className="flex items-center bg-teal-600/30 text-teal-300 px-3 py-1 rounded-full text-xs font-medium">
            <span className="mr-1.5">{IconLightBulb}</span>
            {clusterName}
          </div>
        )}
      </div>

      {postText && (
        <p className="text-slate-300 mb-3 whitespace-pre-wrap break-words">{postText}</p>
      )}

      <div className="flex items-center justify-between text-sm">
        <p className="text-slate-500">
          Медиа: <span className={hasMedia ? "text-green-400 font-semibold" : "text-red-400 font-semibold"}>{hasMedia ? 'Да' : 'Нет'}</span>
        </p>
        <a
          href={postLink}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sky-500 hover:text-sky-300 hover:underline transition-colors duration-200"
        >
          Смотреть пост &rarr;
        </a>
      </div>
    </div>
  );
};

export default PostCard;