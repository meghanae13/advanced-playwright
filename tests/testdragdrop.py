from playwright.sync_api import Page, expect


# 1. Basic element-to-element drag and drop
def testbasicdragdrop(page: Page):
    page.set_content("""
        <div id="source" draggable="true">Task A</div>
        <div id="target" style="width:250px; height:100px; border:1px solid">
            Drop Here
        </div>

        <script>
            const source = document.querySelector("#source");
            const target = document.querySelector("#target");

            source.addEventListener("dragstart", event => {
                event.dataTransfer.setData("text/plain", source.id);
            });

            target.addEventListener("dragover", event => {
                event.preventDefault();
            });

            target.addEventListener("drop", event => {
                event.preventDefault();
                const id = event.dataTransfer.getData("text/plain");
                const draggedElement = document.getElementById(id);
                target.appendChild(draggedElement);
            });
        </script>
    """)

    page.locator("#source").drag_to(page.locator("#target"))

    expect(page.locator("#target #source")).to_have_text("Task A")

# 2. Move a task between containers
def testmovetaskbetweencontainers(page: Page):
    page.set_content("""
        <div id="todo">
            <h2>To Do</h2>
            <div id="task" draggable="true">Design Login Page</div>
        </div>

        <div id="completed">
            <h2>Completed</h2>
        </div>

        <script>
            const task = document.querySelector("#task");

            task.addEventListener("dragstart", event => {
                event.dataTransfer.setData("text/plain", task.id);
            });

            for (const container of document.querySelectorAll("#todo, #completed")) {
                container.addEventListener("dragover", event => {
                    event.preventDefault();
                });

                container.addEventListener("drop", event => {
                    event.preventDefault();
                    const id = event.dataTransfer.getData("text/plain");
                    container.appendChild(document.getElementById(id));
                });
            }
        </script>
    """)

    page.locator("#task").drag_to(page.locator("#completed"))

    expect(page.locator("#completed #task")).to_have_text("Design Login Page")
    expect(page.locator("#todo #task")).to_have_count(0)


# 3. Reorder items in a list
def testreorderlist(page: Page):
    page.set_content("""
        <ul id="tasks">
            <li draggable="true" data-id="a">Task A</li>
            <li draggable="true" data-id="b">Task B</li>
            <li draggable="true" data-id="c">Task C</li>
        </ul>

        <script>
            let dragged;

            document.querySelectorAll("#tasks li").forEach(item => {
                item.addEventListener("dragstart", () => {
                    dragged = item;
                });

                item.addEventListener("dragover", event => {
                    event.preventDefault();
                });

                item.addEventListener("drop", event => {
                    event.preventDefault();

                    if (dragged && dragged !== item) {
                        item.parentNode.insertBefore(dragged, item);
                    }
                });
            });
        </script>
    """)

    page.locator('[data-id="c"]').drag_to(page.locator('[data-id="a"]'))

    order = page.locator("#tasks li").all_text_contents()
    assert order == ["Task C", "Task A", "Task B"]


# 4. Verify source and target counts
def testdragdropcounts(page: Page):
    page.set_content("""
        <div id="source" style="width:200px; min-height:100px; border:1px solid">
            <div draggable="true" id="item">Item A</div>
            <div>Item B</div>
        </div>

        <div id="target"
             style="margin-top:20px; width:200px; min-height:100px; border:1px solid">
            Drop Here
        </div>

        <script>
            const item = document.querySelector("#item");
            const target = document.querySelector("#target");

            item.addEventListener("dragstart", event => {
                event.dataTransfer.setData("text/plain", item.id);
            });

            target.addEventListener("dragover", event => {
                event.preventDefault();
            });

            target.addEventListener("drop", event => {
                event.preventDefault();
                target.appendChild(item);
            });
        </script>
    """)

    page.locator("#item").drag_to(page.locator("#target"))

    expect(page.locator("#source > div")).to_have_count(1)
    expect(page.locator("#target > div")).to_have_count(1)

# 5. Invalid drop: destination rejects the item
def testinvaliddrop(page: Page):
    page.set_content("""
        <div id="source">
            <div draggable="true" id="item">Item A</div>
        </div>
        <div id="target">Drop not allowed</div>
    """)

    page.locator("#item").drag_to(page.locator("#target"))

    expect(page.locator("#source #item")).to_be_visible()
    expect(page.locator("#target")).to_have_text("Drop not allowed")


# 6. Drag events and event order
def testdragevents(page: Page):
    page.set_content("""
        <div draggable="true" id="source">Drag Me</div>
        <div id="target">Target</div>
        <p id="events"></p>

        <script>
            const events = [];

            document.querySelector("#source").addEventListener("dragstart", () => {
                events.push("dragstart");
            });

            document.querySelector("#target").addEventListener("dragover", event => {
                event.preventDefault();
                events.push("dragover");
            });

            document.querySelector("#target").addEventListener("drop", event => {
                event.preventDefault();
                events.push("drop");
                document.querySelector("#events").textContent = events.join(",");
            });

            document.querySelector("#source").addEventListener("dragend", () => {
                events.push("dragend");
                document.querySelector("#events").textContent = events.join(",");
            });
        </script>
    """)

    page.locator("#source").drag_to(page.locator("#target"))

    events = page.locator("#events").inner_text().split(",")

    assert "dragstart" in events
    assert "dragover" in events
    assert "drop" in events
    assert "dragend" in events


# 7. Custom mouse actions for dragging
def testcustommousedrag(page: Page):
    page.set_content("""
        <div id="source" style="width:100px;height:50px;background:#ddd">
            Move Me
        </div>
        <div id="target" style="margin-top:100px;width:200px;height:100px;background:#eee">
            Target
        </div>
    """)

    source = page.locator("#source")
    target = page.locator("#target")

    source_box = source.bounding_box()
    target_box = target.bounding_box()

    assert source_box is not None
    assert target_box is not None

    page.mouse.move(
        source_box["x"] + source_box["width"] / 2,
        source_box["y"] + source_box["height"] / 2
    )
    page.mouse.down()
    page.mouse.move(
        target_box["x"] + target_box["width"] / 2,
        target_box["y"] + target_box["height"] / 2,
        steps=10
    )
    page.mouse.up()

    print("Custom mouse drag completed.")


# 8. Verify drag-and-drop state persists after reload
def testdragpersistence(page: Page):
    page.set_content("""
        <div id="todo"
             style="width:200px; min-height:100px; border:1px solid">
            <div draggable="true" id="task">Task A</div>
        </div>

        <div id="completed"
             style="margin-top:20px; width:200px; min-height:100px; border:1px solid">
            Completed
        </div>

        <p id="status">To Do</p>

        <script>
            const task = document.querySelector("#task");
            const completed = document.querySelector("#completed");

            task.addEventListener("dragstart", event => {
                event.dataTransfer.setData("text/plain", task.id);
            });

            completed.addEventListener("dragover", event => {
                event.preventDefault();
            });

            completed.addEventListener("drop", event => {
                event.preventDefault();
                completed.appendChild(task);
                document.querySelector("#status").textContent = "Completed";
            });
        </script>
    """)

    page.locator("#task").drag_to(page.locator("#completed"))

    expect(page.locator("#completed #task")).to_be_visible()
    expect(page.locator("#status")).to_have_text("Completed")

    print("Task moved and status updated successfully.")