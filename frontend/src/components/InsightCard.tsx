import { Loader2, Sparkles } from "lucide-react";
import type { AxiosError } from "axios";
import type { UseQueryResult } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Insight } from "@/hooks/useInsights";

interface Props {
  title: string;
  query: UseQueryResult<Insight, unknown>;
  enabled: boolean;
  setEnabled: (value: boolean) => void;
}

export default function InsightCard({
  title,
  query,
  enabled,
  setEnabled,
}: Props) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between gap-2">
          <CardTitle className="flex items-center gap-2 text-lg">
            <Sparkles className="h-4 w-4" />
            {title}
          </CardTitle>
          {enabled && query.data && (
            <Button
              size="sm"
              variant="ghost"
              onClick={() => query.refetch()}
              disabled={query.isFetching}
            >
              {query.isFetching ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Regenerating
                </>
              ) : (
                "Regenerate"
              )}
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent>
        <InsightBody
          query={query}
          enabled={enabled}
          onEnable={() => setEnabled(true)}
        />
      </CardContent>
    </Card>
  );
}

function InsightBody({
  query,
  enabled,
  onEnable,
}: {
  query: UseQueryResult<Insight, unknown>;
  enabled: boolean;
  onEnable: () => void;
}) {
  if (!enabled) {
    return (
      <div className="flex flex-col items-start gap-2">
        <p className="text-sm text-muted-foreground">
          Generate an AI summary. Runs on a local Ollama model; first request
          may take 10-20 seconds.
        </p>
        <Button size="sm" onClick={onEnable}>
          <Sparkles className="mr-2 h-4 w-4" />
          Generate
        </Button>
      </div>
    );
  }

  if (query.isLoading || query.isFetching) {
    return (
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Loader2 className="h-4 w-4 animate-spin" />
        <span>Asking the model — this can take up to a minute.</span>
      </div>
    );
  }

  if (query.error) {
    const status = (query.error as AxiosError)?.response?.status;
    if (status === 503) {
      return (
        <p className="text-sm text-muted-foreground">
          AI summary is unavailable. The LLM backend is not reachable.
        </p>
      );
    }
    return (
      <p className="text-sm text-destructive">
        Something went wrong generating the summary.
      </p>
    );
  }

  if (!query.data) {
    return null;
  }

  return (
    <div className="space-y-2">
      <p className="whitespace-pre-wrap text-sm leading-relaxed">
        {query.data.text}
      </p>
      <p className="text-xs text-muted-foreground">
        {query.data.llm_model}
        {query.data.cached ? " · cached" : ""}
      </p>
    </div>
  );
}
