import { Post, ChannelUsername } from '../types';

const API_BASE_URL = 'http://localhost:8000/api/v1';

// Fallback mock data for development
const MOCK_POST_TEXTS: string[] = [
  "Just released a new update! Check out the features. #newrelease",
  "Big news coming next week. Stay tuned! 🚀",
  "Here's a quick recap of today's market trends. #finance",
  "Found this amazing recipe for vegan pasta. 🍝 #food #vegan",
  "Our team is growing! We're hiring a new software engineer. #jobs",
  "What are your thoughts on the latest AI developments? #AI #discussion",
  "Throwback to our first product launch! #TBT",
  "A deep dive into quantum computing applications. #science #tech",
  "Weekend vibes! What are your plans? ☀️",
  "Funny meme compilation to brighten your day! 😂 #memes"
];

const generateMockPosts = (channelName: ChannelUsername): Post[] => {
  const posts: Post[] = [];
  const numPosts = Math.floor(Math.random() * 5) + 1; // 1 to 5 posts per channel

  for (let i = 0; i < numPosts; i++) {
    const now = new Date();
    // Simulate posts from the last 24 hours
    const randomPastMilliseconds = Math.random() * 24 * 60 * 60 * 1000;
    const publicationDate = new Date(now.getTime() - randomPastMilliseconds);

    posts.push({
      id: `${channelName}_${publicationDate.getTime()}_${i}`,
      channelName,
      publicationDateTime: publicationDate.toISOString(),
      postLink: `https://t.me/${channelName}/${Math.floor(Math.random() * 10000)}`,
      postText: MOCK_POST_TEXTS[Math.floor(Math.random() * MOCK_POST_TEXTS.length)],
      hasMedia: Math.random() > 0.5,
      clusterName: "Некатегоризованные", // Mock cluster name
    });
  }
  return posts;
};

const generateMockPostsForChannels = (channels: ChannelUsername[]): Post[] => {
  let allPosts: Post[] = [];
  channels.forEach(channelName => {
    allPosts = allPosts.concat(generateMockPosts(channelName));
  });

  // Sort posts by date, newest first
  allPosts.sort((a, b) => new Date(b.publicationDateTime).getTime() - new Date(a.publicationDateTime).getTime());
  
  return allPosts;
};

export const fetchRecentPosts = async (
  channels: ChannelUsername[]
): Promise<Post[]> => {
  try {
    console.log(`Fetching posts from backend for channels: ${channels.join(', ')}`);
    
    // Check if backend is available
    const healthResponse = await fetch(`${API_BASE_URL}/health`);
    if (!healthResponse.ok) {
      throw new Error('Backend not available');
    }

    // Make request to backend - it returns already clustered posts
    const response = await fetch(`${API_BASE_URL}/posts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        channels: channels,
        hours_back: 24
      })
    });

    if (!response.ok) {
      throw new Error(`Backend error: ${response.status}`);
    }

    const data = await response.json();
    console.log(`Backend returned ${data.total_count} posts in ${data.processing_time_seconds.toFixed(2)}s`);
    
    // Convert backend response to frontend format
    return data.posts.map((post: any) => ({
      id: post.id,
      channelName: post.channelName || post.channel_name,
      publicationDateTime: post.publicationDateTime || post.publication_datetime,
      postLink: post.postLink || post.post_link,
      postText: post.postText || post.post_text,
      hasMedia: post.hasMedia !== undefined ? post.hasMedia : post.has_media,
      clusterName: post.clusterName || post.cluster_name || "Некатегоризованные",
    }));

  } catch (error) {
    console.warn('Backend not available, using mock data:', error);
    
    // Fallback to mock data
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 1000));
    const mockPosts = generateMockPostsForChannels(channels);
    console.log(`Generated ${mockPosts.length} mock posts.`);
    return mockPosts;
  }
};
