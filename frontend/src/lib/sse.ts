import type { StreamEvent, StreamEventType } from "./types";

export function parseSSEChunk(buffer: string): { events: StreamEvent[]; remainder: string } {
  const events: StreamEvent[] = [];
  const blocks = buffer.split("\n\n");

  let remainder = "";
  if (!buffer.endsWith("\n\n") && blocks.length > 0) {
    remainder = blocks.pop() ?? "";
  }

  for (const block of blocks) {
    if (!block.trim()) continue;

    let eventType: StreamEventType | null = null;
    let dataStr = "";

    for (const line of block.split("\n")) {
      if (line.startsWith("event:")) {
        eventType = line.slice(6).trim() as StreamEventType;
      } else if (line.startsWith("data:")) {
        dataStr += line.slice(5).trim();
      }
    }

    if (!eventType || !dataStr) continue;

    try {
      events.push({ event: eventType, data: JSON.parse(dataStr) });
    } catch {
      events.push({ event: eventType, data: dataStr });
    }
  }

  return { events, remainder };
}
