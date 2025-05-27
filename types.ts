
export interface Post {
  id: string;
  channelName: string;
  publicationDateTime: string; // ISO string
  postLink: string;
  postText: string | null;
  hasMedia: boolean;
  clusterName: string | null;
}

// Raw post typically before clustering or full processing
export interface RawPost {
  id: string;
  channelName: string;
  publicationDateTime: string; // ISO string
  postLink: string;
  postText: string | null;
  hasMedia: boolean;
}

export type ChannelUsername = string;
