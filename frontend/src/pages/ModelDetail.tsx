import { useParams, Link } from "react-router";
import { useModel } from "@/hooks/useModel";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function ModelDetail() {
  const { id } = useParams();
  const { data: model, isLoading, error } = useModel(Number(id));

  if (isLoading) {
    return <p className="text-muted-foreground">Loading model...</p>;
  }

  if (error || !model) {
    return <p className="text-destructive">Model not found.</p>;
  }

  return (
    <div>
      <div className="mb-6">
        <Button variant="ghost" asChild>
          <Link to="/">&larr; Back to models</Link>
        </Button>
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-2xl">{model.name}</CardTitle>
              <p className="text-muted-foreground">{model.provider.name}</p>
            </div>
            <div className="flex gap-1.5">
              {model.is_open_source && (
                <Badge variant="secondary">Open Source</Badge>
              )}
              {model.arena_elo_score && (
                <Badge variant="outline">ELO {model.arena_elo_score}</Badge>
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {model.description && (
            <div>
              <h3 className="mb-1 text-sm font-medium text-muted-foreground">
                Description
              </h3>
              <p>{model.description}</p>
            </div>
          )}

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <div>
              <p className="text-sm text-muted-foreground">Context Window</p>
              <p className="text-lg font-medium">
                {(model.context_window / 1000).toLocaleString()}K tokens
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Input Price</p>
              <p className="text-lg font-medium">
                ${parseFloat(model.input_price_per_1m)}/1M tokens
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Output Price</p>
              <p className="text-lg font-medium">
                ${parseFloat(model.output_price_per_1m)}/1M tokens
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Release Date</p>
              <p className="text-lg font-medium">{model.release_date}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
