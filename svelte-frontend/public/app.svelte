<script>
    import { onMount } from "svelte";
    import { writable } from "svelte/store";
    import { format } from "date-fns";

    let classes = writable([]);
    let classType = "canvas";
    let courseId = "";
    let fileId = "";

    let assignments = writable([]);

    const addClass = () => {
        classes.update((cls) => [
            ...cls,
            { type: classType, course_id: courseId, file_id: fileId },
        ]);
        courseId = "";
        fileId = "";
    };

    const fetchAssignments = async () => {
        const response = await fetch(
            "http://127.0.0.1:5000/fetch-assignments",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ classes: $classes }),
            },
        );
        const data = await response.json();
        assignments.set(data);
    };
</script>

<div class="container">
    <div class="content">
        <h1>Add Classes</h1>
        <div>
            <label for="classType">Class Type</label>
            <select bind:value={classType} id="classType">
                <option value="canvas">Canvas</option>
                <option value="docx">DOCX</option>
                <option value="pdf">PDF</option>
            </select>
        </div>

        <div>
            <label for="courseId">Course ID</label>
            <input
                type="text"
                bind:value={courseId}
                id="courseId"
                placeholder="Enter Course ID"
            />
        </div>

        {#if classType !== "canvas"}
            <div>
                <label for="fileId">File ID</label>
                <input
                    type="text"
                    bind:value={fileId}
                    id="fileId"
                    placeholder="Enter File ID"
                />
            </div>
        {/if}

        <button on:click={addClass}>Add Class</button>
        <button on:click={fetchAssignments}>Run</button>

        <h2>Class List</h2>
        <ul>
            {#each $classes as cls}
                <li>
                    {cls.type}: {cls.course_id}
                    {cls.file_id && ` | File ID: ${cls.file_id}`}
                </li>
            {/each}
        </ul>
    </div>

    <div class="sidebar">
        <h2>Assignments Due Today</h2>
        <div class="assignment-list">
            {#each $assignments as assignment}
                <div class="assignment">
                    <h3>{assignment.title}</h3>
                    <p>{assignment.description}</p>
                    <small>Due: {assignment.due_date}</small>
                </div>
            {/each}
        </div>
    </div>
</div>

<style>
    /* Simple styling for the layout */
    .container {
        display: flex;
    }
    .sidebar {
        width: 25%;
        padding: 20px;
        background-color: #f4f4f4;
    }
    .content {
        width: 75%;
        padding: 20px;
    }
    .assignment-list {
        margin-top: 20px;
    }
    .assignment {
        padding: 10px;
        margin-bottom: 10px;
        border: 1px solid #ddd;
        border-radius: 5px;
    }
</style>
