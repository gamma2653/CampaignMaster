import { createFileRoute, useRouter } from '@tanstack/react-router';
import { usePointByID } from '../../../../../../query';
import { formOptions } from '@tanstack/react-form';
import { useAppForm } from '../../../../../../features/shared/components/ctx';
import {
  PointGroup,
  defaultValues,
} from '../../../../../../features/shared/components/fieldgroups/PointGroup';
import { PREFIXES } from '../../../../../../schemas';

export const Route = createFileRoute(
  '/campaign/plan/$camp_id/point/$point_id/',
)({
  component: PointDetailComponent,
});

function PointDetailComponent() {
  const { point_id } = Route.useParams();
  const router = useRouter();
  const pointID = {
    prefix: PREFIXES.POINT,
    numeric: parseInt(point_id),
  };

  const { data: point, isLoading, error } = usePointByID(pointID);

  const pointOpts = formOptions({
    defaultValues: point || defaultValues,
    onSubmit: async ({ value }) => {
      try {
        const response = await fetch(`/api/campaign/p/${point_id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            obj_id: value.obj_id,
            name: value.name,
            description: value.description,
            objective: value.objective,
          }),
        });

        if (response.ok) {
          alert('Point updated successfully!');
          router.invalidate();
        } else {
          alert('Failed to update point');
        }
      } catch {
        alert('Error updating point');
      }
    },
  });

  const form = useAppForm(pointOpts);

  if (isLoading) return <div className="p-4">Loading point...</div>;
  if (error) return <div className="p-4 text-red-500">Error loading point</div>;
  if (!point) return <div className="p-4">Point not found</div>;

  return (
    <div className="p-4 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Edit Point</h1>

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
              label="Update Point"
              className="self-center submit-button"
            />
          </div>
        </form.AppForm>
      </form>
    </div>
  );
}
