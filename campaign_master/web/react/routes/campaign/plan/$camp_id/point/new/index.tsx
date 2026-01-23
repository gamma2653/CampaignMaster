import { createFileRoute, useRouter } from '@tanstack/react-router';
import { formOptions } from '@tanstack/react-form';
import { useAppForm } from '../../../../../../features/shared/components/ctx';
import {
  PointGroup,
  defaultValues,
} from '../../../../../../features/shared/components/fieldgroups/PointGroup';

export const Route = createFileRoute('/campaign/plan/$camp_id/point/new/')({
  component: PointCreateComponent,
});

function PointCreateComponent() {
  const { camp_id } = Route.useParams();
  const router = useRouter();

  const pointOpts = formOptions({
    defaultValues,
    onSubmit: async ({ value }) => {
      try {
        const response = await fetch('/api/campaign/p', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            name: value.name,
            description: value.description,
            objective: value.objective,
          }),
        });

        if (response.ok) {
          const created = await response.json();
          alert('Point created successfully!');
          router.navigate({
            to: '/campaign/plan/$camp_id/point/$point_id',
            params: {
              camp_id,
              point_id: created.obj_id.numeric.toString(),
            },
          });
        } else {
          alert('Failed to create point');
        }
      } catch {
        alert('Error creating point');
      }
    },
  });

  const form = useAppForm(pointOpts);

  return (
    <div className="p-4 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Create New Point</h1>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          e.stopPropagation();
          form.handleSubmit();
        }}
        className="space-y-4"
      >
        <PointGroup form={form} fields={defaultValues} />

        <form.AppForm>
          <div className="flex flex-col p-2 pb-8">
            <form.SubscribeButton
              label="Create Point"
              className="self-center submit-button"
            />
          </div>
        </form.AppForm>
      </form>
    </div>
  );
}
