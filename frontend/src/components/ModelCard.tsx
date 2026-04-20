import { Link } from "react-router";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import type { LLMModelListItem } from "@/types";

interface ModelCardProps {
  model: LLMModelListItem;
}

export default function ModelCard({ model }: ModelCardProps) {
  return (
    <Link to={`/models/${model.id}`} className="block">
      <Card className="transition-colors hover:bg-accent/50">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-base">{model.name}</CardTitle>
              <p className="text-sm text-muted-foreground">
                {model.provider.name}
              </p>
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
        <CardContent>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <p className="text-muted-foreground">Context</p>
              <p className="font-medium">
                {(model.context_window / 1000).toLocaleString()}K
              </p>
            </div>
            <div>
              <p className="text-muted-foreground">Input</p>
              <p className="font-medium">
                ${parseFloat(model.input_price_per_1m)}/1M
              </p>
            </div>
            <div>
              <p className="text-muted-foreground">Output</p>
              <p className="font-medium">
                ${parseFloat(model.output_price_per_1m)}/1M
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
