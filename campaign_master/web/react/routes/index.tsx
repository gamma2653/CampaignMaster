import { createFileRoute } from '@tanstack/react-router';

const HomeComponent = () => {
  return (
    <div>
      <h1>Campaign Master</h1>
    </div>
  );
};

export const Route = createFileRoute('/')({
  component: HomeComponent,
});
