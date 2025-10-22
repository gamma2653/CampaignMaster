import { createFileRoute } from '@tanstack/react-router'

import { ChoicePage } from '../components/ChoicePage'

export const Route = createFileRoute('/')({
  component: HomeComponent,
})

function HomeComponent() {
  const handleChoose = (value: string) => {
    // Navigate to the selected route
    
  };

  return (
    <ChoicePage
      title="Welcome to Campaign Master"
      description="Choose an option to get started:"
      choices={[
        { label: 'Create Campaign Plan', value: 'create-campaign' },
        { label: 'Load Existing Campaign', value: 'load-campaign' },
      ]}
      onChoose={handleChoose}
    />
  )
}