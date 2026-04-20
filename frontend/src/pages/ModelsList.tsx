import { useModels } from "@/hooks/useModels";
import ModelCard from "@/components/ModelCard";

export default function ModelsList() {
  const { data: models, isLoading, error } = useModels();

  if (isLoading) {
    return <p className="text-muted-foreground">Loading models...</p>;
  }

  if (error) {
    return <p className="text-destructive">Failed to load models.</p>;
  }

  return (
    <div>
      <h1 className="mb-6 text-2xl font-bold">Models</h1>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {models?.map((model) => (
          <ModelCard key={model.id} model={model} />
        ))}
      </div>
    </div>
  );
}
