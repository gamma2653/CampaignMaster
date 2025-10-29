import { CampaignSchema, Campaign, Point, PointSchema } from "../schemas";
import { useForm } from "@tanstack/react-form";
import { z } from "zod";



async function defaultValues(): Promise<Campaign> {
    const obj_id = await fetch("/api/planning/campaigns/new_id").then(res => res.json()).then(data => {
        return data as Campaign["obj_id"];
    });
    return {
        obj_id: {
            prefix: "CAMP",
            numeric: 0,
        },
        title: "",
        version: "",
        setting: "",
        summary: "",
        storypoints: [],
        characters: [],
        locations: [],
        items: [],
        rules: [],
        objectives: [],
    };
}


function CampaignForm(){
    const form = useForm({
        defaultValues: defaultValues(),
        validators: {
            onChange: CampaignSchema,
        },
        onSubmit: async ({ value }) => {
            console.log("Submitted campaign:", value);
        },

    });

    return (
        <form
            onSubmit={(e) => {
                e.preventDefault();
                form.handleSubmit();
            }}
        >
            
        </form>
    );

}




async function defaultPointValues(): Promise<Point> {
    const obj_id = await fetch("/api/planning/campaigns/new_id").then(res => res.json()).then(data => {
        return data as Point["obj_id"];
    });
    return {
        obj_id,
        name: "",
        description: "",
        objective: undefined,
    };
}


function PointForm(){
    const form = useForm({
        defaultValues: defaultPointValues(),
        validators: {
            onChange: PointSchema.safeParse,
        },
        onSubmit: async ({ value }) => {
            console.log("Submitted point:", value);
        },

    });

    return (
        <form
            onSubmit={(e) => {
                e.preventDefault();
                form.handleSubmit();
            }}
        >
            
        </form>
    );

}