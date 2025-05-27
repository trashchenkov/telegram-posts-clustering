import { Post, RawPost } from '../types';

// This service is now simplified since clustering happens in the backend automatically
// We keep it for backward compatibility and potential future use

export const clusterPostsWithGemini = async (
  rawPosts: RawPost[]
): Promise<Post[]> => {
  // Since our backend now returns already clustered posts,
  // this function is mainly for fallback scenarios
  
  console.log("Converting raw posts to clustered posts (fallback)");
  
  // Simple fallback clustering based on keywords
  return rawPosts.map(rawPost => {
    let clusterName = "Некатегоризованные";
    
    if (rawPost.postText) {
      const text = rawPost.postText.toLowerCase();
      
      if (text.includes('ai') || text.includes('ии') || text.includes('нейро') || text.includes('ml') || text.includes('openai') || text.includes('anthropic')) {
        clusterName = "Искусственный интеллект";
      } else if (text.includes('работа') || text.includes('вакансия') || text.includes('hiring') || text.includes('job')) {
        clusterName = "Вакансии";
      } else if (text.includes('новости') || text.includes('news') || text.includes('обновление') || text.includes('релиз')) {
        clusterName = "Новости";
      } else if (text.includes('мем') || text.includes('😂') || text.includes('🤣') || text.includes('funny')) {
        clusterName = "Мемы";
      } else if (text.includes('крипто') || text.includes('bitcoin') || text.includes('блокчейн')) {
        clusterName = "Криптовалюты";
      } else if (text.includes('код') || text.includes('программ') || text.includes('разработ') || text.includes('python') || text.includes('javascript')) {
        clusterName = "Разработка";
      } else if (text.includes('стартап') || text.includes('бизнес') || text.includes('инвест')) {
        clusterName = "Бизнес";
      } else if (text.includes('курс') || text.includes('обучение') || text.includes('туториал')) {
        clusterName = "Образование";
      }
    }
    
    return {
      ...rawPost,
      clusterName: clusterName,
    };
  });
};

// New function to get clustering statistics
export const getClusteringStats = (posts: Post[]) => {
  const clusterCounts: { [key: string]: number } = {};
  
  posts.forEach(post => {
    const clusterName = post.clusterName || "Некатегоризованные";
    clusterCounts[clusterName] = (clusterCounts[clusterName] || 0) + 1;
  });
  
  return Object.entries(clusterCounts)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count);
};
