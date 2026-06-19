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
import android.widget.Button;
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
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class MainActivity extends AppCompatActivity {

    private TextView tvStatus, tvAccountInfo;
    private Button btnRunNoon, btnRunEvening, btnStop, btnInitEnv;
    private boolean isRunning = false;
    private final ExecutorService executor = Executors.newSingleThreadExecutor();
    private final Handler handler = new Handler(Looper.getMainLooper());
    private static final int STORAGE_PERMISSION_CODE = 1000;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        if (!Python.isStarted()) {
            Python.start(new AndroidPlatform(this));
        }

        tvStatus      = findViewById(R.id.tvStatus);
        tvAccountInfo = findViewById(R.id.tvAccountInfo);
        btnRunNoon    = findViewById(R.id.btnRunNoon);
        btnRunEvening = findViewById(R.id.btnRunEvening);
        btnStop       = findViewById(R.id.btnStop);
        btnInitEnv    = findViewById(R.id.btnInitEnv);

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

        checkStoragePermission();
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
                File externalDir = new File(Environment.getExternalStorageDirectory(), "AwuweiDDL");
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
                Toast.makeText(this, "请先授予所有文件管理权限", Toast.LENGTH_SHORT).show();
                checkStoragePermission();
                return;
            }
        } else {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
                Toast.makeText(this, "请先授予存储权限", Toast.LENGTH_SHORT).show();
                checkStoragePermission();
                return;
            }
        }

        executor.execute(() -> {
            try {
                File externalDir = new File(Environment.getExternalStorageDirectory(), "AwuweiDDL");
                String message;
                if (!externalDir.exists()) {
                    if (externalDir.mkdirs()) {
                        message = "已创建 AwuweiDDL 文件夹并释放模板文件";
                    } else {
                        message = "文件夹创建失败，请检查权限";
                    }
                } else {
                    message = "配置文件夹已存在：" + externalDir.getAbsolutePath();
                }

                PyObject bridge = Python.getInstance().getModule("bridge");
                bridge.callAttr("init_app", externalDir.getAbsolutePath());
                
                handler.post(() -> Toast.makeText(this, message, Toast.LENGTH_LONG).show());
                loadAccountInfo();
            } catch (Exception e) {
                handler.post(() -> Toast.makeText(this, "初始化异常: " + e.getMessage(), Toast.LENGTH_LONG).show());
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
                String info = bridge.callAttr("get_account_summary").toString();
                handler.post(() -> tvAccountInfo.setText(info));
            } catch (Exception e) {
                handler.post(() -> tvAccountInfo.setText("账号信息加载失败"));
            }
        });
    }

    private void runTask(String module) {
        if (isRunning) return;
        isRunning = true;
        setRunningState(true, module.equals("noon") ? "🌞 执行午间任务中..." : "🌙 执行晚间任务中...");
        executor.execute(() -> {
            try {
                PyObject bridge = Python.getInstance().getModule("bridge");
                bridge.callAttr("run_module", module);
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
