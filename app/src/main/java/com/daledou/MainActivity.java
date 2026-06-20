package com.daledou;

import android.Manifest;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;
import java.io.File;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class MainActivity extends AppCompatActivity {

    private TextView tvStatus, tvAccountInfo;
    private Button btnRunNoon, btnRunEvening, btnStop, btnInitEnv;
    private Spinner spAccounts;
    private boolean isRunning = false;
    private final ExecutorService executor = Executors.newSingleThreadExecutor();
    private final Handler handler = new Handler(Looper.getMainLooper());
    private static final int STORAGE_PERMISSION_CODE = 1000;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // 使用 AppConfig 动态设置标题
        TextView tvTitle = findViewById(R.id.tvTitle);
        if (tvTitle != null) tvTitle.setText("🎮 " + AppConfig.APP_NAME);

        if (!Python.isStarted()) {
            Python.start(new AndroidPlatform(this));
        }

        tvStatus      = findViewById(R.id.tvStatus);
        tvAccountInfo = findViewById(R.id.tvAccountInfo);
        btnRunNoon    = findViewById(R.id.btnRunNoon);
        btnRunEvening = findViewById(R.id.btnRunEvening);
        btnStop       = findViewById(R.id.btnStop);
        btnInitEnv    = findViewById(R.id.btnInitEnv);
        spAccounts    = findViewById(R.id.spAccounts);
        Button btnRefreshAccounts = findViewById(R.id.btnRefreshAccounts);

        findViewById(R.id.btnCookie).setOnClickListener(v ->
            startActivity(new Intent(this, CookieActivity.class)));
        findViewById(R.id.btnConfig).setOnClickListener(v ->
            startActivity(new Intent(this, ConfigMainActivity.class)));
        findViewById(R.id.btnLog).setOnClickListener(v ->
            startActivity(new Intent(this, LogActivity.class)));
        findViewById(R.id.btnTest).setOnClickListener(v ->
            startActivity(new Intent(this, TestActivity.class)));

        btnRunNoon.setOnClickListener(v -> checkPermissionAndRun("noon"));
        btnRunEvening.setOnClickListener(v -> checkPermissionAndRun("evening"));
        btnStop.setOnClickListener(v -> stopTask());
        
        btnInitEnv.setOnClickListener(v -> handleManualInit());
        btnRefreshAccounts.setOnClickListener(v -> loadAccountInfo());
        
        findViewById(R.id.btnDeleteAccount).setOnClickListener(v -> confirmDeleteAccount());

        checkStoragePermission();
    }

    private void confirmDeleteAccount() {
        String selectedQq = spAccounts.getSelectedItem() != null ? spAccounts.getSelectedItem().toString() : "";
        if (selectedQq.isEmpty() || selectedQq.contains("请先配置")) return;
        
        new androidx.appcompat.app.AlertDialog.Builder(this)
                .setTitle("⚠️ 确认删除")
                .setMessage("是否确认删除账号: " + selectedQq + "？\n此操作仅从应用列表中移除。")
                .setPositiveButton("确认删除", (dialog, which) -> {
                    executor.execute(() -> {
                        try {
                            PyObject bridge = Python.getInstance().getModule("bridge");
                            bridge.callAttr("delete_cookie", selectedQq);
                            handler.post(() -> {
                                Toast.makeText(this, "✅ 账号已删除", Toast.LENGTH_SHORT).show();
                                loadAccountInfo();
                            });
                        } catch (Exception e) {
                            handler.post(() -> Toast.makeText(this, "❌ 删除失败: " + e.getMessage(), Toast.LENGTH_SHORT).show());
                        }
                    });
                })
                .setNegativeButton("取消", null)
                .show();
    }

    private void checkStoragePermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            if (!Environment.isExternalStorageManager()) {
                Intent intent = new Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION);
                intent.setData(Uri.parse("package:" + getPackageName()));
                startActivity(intent);
            }
        } else {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.WRITE_EXTERNAL_STORAGE}, STORAGE_PERMISSION_CODE);
            }
        }
        initPythonPath();
    }

    private void initPythonPath() {
        executor.execute(() -> {
            try {
                File externalDir = new File(Environment.getExternalStorageDirectory(), AppConfig.CONF_DIR_NAME);
                if (!externalDir.exists()) externalDir.mkdirs();
                
                PyObject bridge = Python.getInstance().getModule("bridge");
                bridge.callAttr("init_app", externalDir.getAbsolutePath());
                loadAccountInfo();
            } catch (Exception e) {
                e.printStackTrace();
            }
        });
    }

    private void handleManualInit() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            if (!Environment.isExternalStorageManager()) {
                checkStoragePermission();
                return;
            }
        } else {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
                checkStoragePermission();
                return;
            }
        }

        executor.execute(() -> {
            try {
                File externalDir = new File(Environment.getExternalStorageDirectory(), AppConfig.CONF_DIR_NAME);
                if (!externalDir.exists()) {
                    externalDir.mkdirs();
                }

                PyObject bridge = Python.getInstance().getModule("bridge");
                bridge.callAttr("init_app", externalDir.getAbsolutePath());
                
                handler.post(() -> {
                    Toast.makeText(this, "✅ 环境初始化完成", Toast.LENGTH_SHORT).show();
                    loadAccountInfo();
                });
            } catch (Exception e) {
                handler.post(() -> Toast.makeText(this, "❌ 初始化失败: " + e.getMessage(), Toast.LENGTH_SHORT).show());
            }
        });
    }

    private void checkPermissionAndRun(String module) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            if (Environment.isExternalStorageManager()) {
                runTask(module);
            } else {
                Toast.makeText(this, "需要存储权限以读写配置文件", Toast.LENGTH_SHORT).show();
            }
        } else {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE) == PackageManager.PERMISSION_GRANTED) {
                runTask(module);
            } else {
                ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.WRITE_EXTERNAL_STORAGE}, STORAGE_PERMISSION_CODE);
            }
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        loadAccountInfo();
    }

    private void loadAccountInfo() {
        executor.execute(() -> {
            try {
                PyObject bridge = Python.getInstance().getModule("bridge");
                String qqListStr = bridge.callAttr("get_qq_list").toString();
                String[] qqArray = qqListStr.split(",");
                List<String> list = new ArrayList<>();
                for (String q : qqArray) if (!q.trim().isEmpty()) list.add(q.trim());
                
                String summary = bridge.callAttr("get_account_summary").toString();
                
                handler.post(() -> {
                    if (list.isEmpty()) {
                        list.add("请先配置 Cookie");
                    }
                    ArrayAdapter<String> adapter = new ArrayAdapter<>(this, android.R.layout.simple_spinner_item, list);
                    adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
                    spAccounts.setAdapter(adapter);
                    tvAccountInfo.setText(summary);
                });
            } catch (Exception e) {
                handler.post(() -> tvAccountInfo.setText("账号信息加载失败"));
            }
        });
    }

    private void runTask(String module) {
        if (isRunning) return;
        
        String selectedQq = spAccounts.getSelectedItem() != null ? spAccounts.getSelectedItem().toString() : "";
        if (selectedQq.contains("请先配置")) {
            Toast.makeText(this, "请先进入 Cookie 界面配置账号", Toast.LENGTH_SHORT).show();
            return;
        }

        isRunning = true;
        setRunningState(true, (module.equals("noon") ? "🌞 执行午间任务 (" : "🌙 执行晚间任务 (") + selectedQq + ")...");
        executor.execute(() -> {
            try {
                PyObject bridge = Python.getInstance().getModule("bridge");
                bridge.callAttr("run_module", module, selectedQq);
                handler.post(() -> setRunningState(false, "✅ 任务执行完成"));
            } catch (Exception e) {
                handler.post(() -> setRunningState(false, "❌ 执行失败: " + e.getMessage()));
            } finally {
                isRunning = false;
            }
        });
    }

    private void stopTask() {
        if (!isRunning) return;
        try {
            PyObject bridge = Python.getInstance().getModule("bridge");
            bridge.callAttr("stop_task");
        } catch (Exception ignored) {}
        isRunning = false;
        setRunningState(false, "⏹ 任务已停止");
    }

    private void setRunningState(boolean running, String msg) {
        isRunning = running;
        tvStatus.setText(msg);
        btnRunNoon.setEnabled(!running);
        btnRunEvening.setEnabled(!running);
        btnStop.setEnabled(running);
        btnStop.setAlpha(running ? 1.0f : 0.5f);
        btnRunNoon.setAlpha(running ? 0.5f : 1.0f);
        btnRunEvening.setAlpha(running ? 0.5f : 1.0f);
    }
}
