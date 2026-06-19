package com.daledou;

import android.content.Context;
import android.os.Handler;
import android.os.Looper;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.LinearLayout;
import android.widget.TextView;

import com.chaquo.python.PyObject;
import com.chaquo.python.Python;

import java.util.LinkedHashMap;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class TaskRegisterPanel {

    private final Context ctx;
    private final LinearLayout taskListContainer;
    private final TextView tvMsg, tvTaskCount;
    private final Button btnModuleNoon, btnModuleEvening;
    private final ExecutorService executor = Executors.newSingleThreadExecutor();
    private final Handler handler = new Handler(Looper.getMainLooper());

    private String currentModule = "noon";
    private final Map<String, CheckBox> taskCheckBoxes = new LinkedHashMap<>();

    public TaskRegisterPanel(Context ctx, View root) {
        this.ctx = ctx;
        taskListContainer = root.findViewById(R.id.taskListContainer);
        tvMsg             = root.findViewById(R.id.tvTaskMsg);
        tvTaskCount       = root.findViewById(R.id.tvTaskCount);
        btnModuleNoon     = root.findViewById(R.id.btnModuleNoon);
        btnModuleEvening  = root.findViewById(R.id.btnModuleEvening);

        root.findViewById(R.id.btnSelectAll).setOnClickListener(v -> setAllChecked(true));
        root.findViewById(R.id.btnSelectNone).setOnClickListener(v -> setAllChecked(false));
        root.findViewById(R.id.btnSaveTasks).setOnClickListener(v -> saveTasks());

        btnModuleNoon.setOnClickListener(v -> switchModule("noon"));
        btnModuleEvening.setOnClickListener(v -> switchModule("evening"));
    }

    public void onShow() {
        loadTasks(currentModule);
    }

    private void switchModule(String module) {
        currentModule = module;
        btnModuleNoon.setBackgroundResource(
            module.equals("noon") ? R.drawable.bg_btn_blue : R.drawable.bg_tab_normal);
        btnModuleNoon.setTextColor(module.equals("noon") ? 0xFFFFFFFF : 0xFF9E9E9E);
        btnModuleEvening.setBackgroundResource(
            module.equals("evening") ? R.drawable.bg_btn_blue : R.drawable.bg_tab_normal);
        btnModuleEvening.setTextColor(module.equals("evening") ? 0xFFFFFFFF : 0xFF9E9E9E);
        loadTasks(module);
    }

    private void loadTasks(String module) {
        executor.execute(() -> {
            try {
                PyObject bridge = Python.getInstance().getModule("bridge");
                String raw = bridge.callAttr("get_task_list", module).toString();
                handler.post(() -> buildTaskUI(raw));
            } catch (Exception e) {
                handler.post(() -> setMsg("❌ 加载任务失败: " + e.getMessage(), false));
            }
        });
    }

    private void buildTaskUI(String raw) {
        taskListContainer.removeAllViews();
        taskCheckBoxes.clear();

        if (raw == null || raw.isEmpty()) {
            setMsg("暂无任务数据", false);
            return;
        }

        LayoutInflater inflater = LayoutInflater.from(ctx);
        int total = 0, enabled = 0;

        for (String item : raw.split(",")) {
            item = item.trim();
            if (item.isEmpty()) continue;
            String[] parts = item.split(":", 2);
            if (parts.length < 2) continue;

            String taskName = parts[0];
            boolean isEnabled = parts[1].equals("1");
            total++;
            if (isEnabled) enabled++;

            View row = inflater.inflate(R.layout.item_task, taskListContainer, false);
            CheckBox cb      = row.findViewById(R.id.cbTask);
            TextView tvName  = row.findViewById(R.id.tvTaskName);
            TextView tvStatus = row.findViewById(R.id.tvTaskStatus);

            cb.setChecked(isEnabled);
            tvName.setText(taskName);

            updateStatusTag(tvStatus, isEnabled);

            row.setOnClickListener(v -> cb.setChecked(!cb.isChecked()));
            cb.setOnCheckedChangeListener((btn, checked) -> updateStatusTag(tvStatus, checked));

            taskCheckBoxes.put(taskName, cb);
            taskListContainer.addView(row);
        }

        int finalEnabled = enabled;
        tvTaskCount.setText(finalEnabled + "/" + total + " 已启用");
        setMsg("✅ 已加载 " + total + " 个任务", true);
    }

    private void updateStatusTag(TextView tv, boolean enabled) {
        if (enabled) {
            tv.setText("已启用");
            tv.setBackgroundResource(R.drawable.bg_tag_green);
            tv.setTextColor(0xFF98FB98);
        } else {
            tv.setText("已禁用");
            tv.setBackgroundResource(R.drawable.bg_tag_grey);
            tv.setTextColor(0xFF9E9E9E);
        }
    }

    private void setAllChecked(boolean checked) {
        for (CheckBox cb : taskCheckBoxes.values()) cb.setChecked(checked);
    }

    private void saveTasks() {
        StringBuilder sb = new StringBuilder();
        for (Map.Entry<String, CheckBox> entry : taskCheckBoxes.entrySet()) {
            if (sb.length() > 0) sb.append(",");
            sb.append(entry.getKey()).append(":").append(entry.getValue().isChecked() ? "1" : "0");
        }
        String data = sb.toString();
        executor.execute(() -> {
            try {
                PyObject bridge = Python.getInstance().getModule("bridge");
                bridge.callAttr("save_task_register", currentModule, data);
                handler.post(() -> {
                    setMsg("✅ 任务注册已保存", true);
                    loadTasks(currentModule);
                });
            } catch (Exception e) {
                handler.post(() -> setMsg("❌ 保存失败: " + e.getMessage(), false));
            }
        });
    }

    private void setMsg(String msg, boolean ok) {
        tvMsg.setText(msg);
        tvMsg.setTextColor(ok ? 0xFF2ECC71 : 0xFFE74C3C);
    }
}
