export type VideoLabel = "A" | "B";

export type VideoPlatform = "youtube" | "instagram";

export type TranscriptStatus = "available" | "partial" | "unavailable";

export type ExtractionStatus = "complete" | "partial" | "failed";

export interface TranscriptSegment {
  start_seconds: number;
  end_seconds: number;
  text: string;
}

export interface NormalizedVideo {
  platform: VideoPlatform;
  url: string;
  video_id: string;
  title?: string | null;
  creator?: string | null;
  upload_date?: string | null;
  duration_seconds?: number | null;
  views?: number | null;
  likes?: number | null;
  comments?: number | null;
  hashtags?: string[] | null;
  follower_count?: number | null;
  engagement_rate?: number | null;
  transcript: TranscriptSegment[];
  transcript_status: TranscriptStatus;
  transcript_source: string;
  metadata_status: ExtractionStatus;
  raw_metadata: Record<string, unknown>;
  warnings: string[];
}

export interface IngestResponse {
  session_id: string;
  youtube: NormalizedVideo;
  instagram: NormalizedVideo;
}

export interface IndexResponse {
  session_id: string;
  chunks_indexed: number;
  skipped_reindex: boolean;
  fingerprint: string;
}

export interface Citation {
  index: number;
  video_label: VideoLabel;
  video_id: string;
  chunk_id: string;
  chunk_index: number;
  start_time: number;
  end_time: number;
  excerpt: string;
  platform: string;
  url: string;
  title?: string | null;
  creator?: string | null;
  score: number;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  citations?: Citation[];
  streaming?: boolean;
  error?: string;
}

export type AnalysisPhase =
  | "idle"
  | "extracting"
  | "indexing"
  | "ready"
  | "error";

export type StreamEventType = "citations" | "token" | "done" | "error";

export interface StreamEvent {
  event: StreamEventType;
  data: unknown;
}
