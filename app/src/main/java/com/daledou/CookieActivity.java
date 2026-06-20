package com.daledou;

import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.content.SharedPreferences;
import android.os.Environment;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStreamReader;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class CookieActivity extends AppCompatActivity {

    private EditText etCookie;
    private TextView tvMsg;
    private final ExecutorService executor = Executors.newSingleThreadExecutor();
    private final Handler handler = new Handler(Looper.getMainLooper());
    private static final String PREF_NAME = "cookie_history";
    private static final String KEY_HISTORY = "history_list";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_cookie);

        etCookie = findViewById(R.id.etCookie);
        tvMsg    = findViewById(R.id.tvMsg);
        Button btnBack = findViewById(R.id.btnBack);
        Button btnSave = findViewById(R.id.btnSave);
        Button btnLocalBackup = findViewById(R.id.btnLocalBackup);
        Button btnLocalRestore = findViewById(R.id.btnLocalRestore);
        Button btnHistory = findViewById(R.id.btnHistory);

        btnBack.setOnClickListener(v -> finish());
        btnSave.setOnClickListener(v -> saveWithHistory());
        
        btnLocalBackup.setOnClickListener(v -> backupToLocal());
        btnLocalRestore.setOnClickListener(v -> restoreFromLocal());
        btnHistory.setOnClickListener(v -> showHistoryDialog());

        // 首次加载不自动填充，保持空白方便输入
        setMsg("请粘贴 Cookie 内容并点击保存", true);
    }

    private void saveWithHistory() {
        String content = etCookie.getText().toString().trim();
        if (content.isEmpty()) {
            setMsg("⚠️ 内容不能为空", false);
            return;
        }
        
        executor.execute(() -> {
            try {
                // 1. 调用 Python 逻辑处理单条保存与列表更新
                PyObject bridge = Python.getInstance().getModule("bridge");
                String qq = bridge.callAttr("save_single_cookie", content).toString();
                
                // 2. 保存到本地 txt 备份 (由 Java 处理)
                saveToLocalTxt(content);
                
                // 3. 保存到历史记录 (SharedPreferences)
                saveToHistory(content);
                
                handler.post(() -> {
                    Toast.makeText(this, "✅ 账号 " + qq + " 已添加并备份到本地", Toast.LENGTH_SHORT).show();
                    setMsg("✅ 保存成功 (账号: " + qq + ")", true);
                });
            } catch (Exception e) {
                handler.post(() -> setMsg("❌ 保存失败: " + e.getMessage(), false));
            }
        });
    }

    private void saveToLocalTxt(String content) {
        try {
            File dir = new File(Environment.getExternalStorageDirectory(), AppConfig.CONF_DIR_NAME);
            if (!dir.exists()) dir.mkdirs();
            File file = new File(dir, AppConfig.COOKIE_BACKUP_FILE);
            
            // 追加模式保存，方便查看所有输入过的
            FileOutputStream fos = new FileOutputStream(file, true);
            fos.write((content + "\n").getBytes());
            fos.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void saveToHistory(String content) {
        SharedPreferences prefs = getSharedPreferences(PREF_NAME, MODE_PRIVATE);
        String historyStr = prefs.getString(KEY_HISTORY, "[]");
        try {
            JSONArray array = new JSONArray(historyStr);
            JSONObject entry = new JSONObject();
            String time = new SimpleDateFormat("MM-dd HH:mm", Locale.getDefault()).format(new Date());
            entry.put("time", time);
            entry.put("content", content);
            
            // 如果内容已存在，则先删除旧的
            for (int i = 0; i < array.length(); i++) {
                if (array.getJSONObject(i).getString("content").equals(content)) {
                    array.remove(i);
                    break;
                }
            }
            
            // 插入到最前面
            JSONArray newArray = new JSONArray();
            newArray.put(entry);
            for (int i = 0; i < array.length() && i < 19; i++) { // 最多保留 20 条
                newArray.put(array.get(i));
            }
            
            prefs.edit().putString(KEY_HISTORY, newArray.toString()).apply();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void showHistoryDialog() {
        SharedPreferences prefs = getSharedPreferences(PREF_NAME, MODE_PRIVATE);
        String historyStr = prefs.getString(KEY_HISTORY, "[]");
        List<String> items = new ArrayList<>();
        List<String> contents = new ArrayList<>();
        try {
            JSONArray array = new JSONArray(historyStr);
            for (int i = 0; i < array.length(); i++) {
                JSONObject obj = array.getJSONObject(i);
                items.add(obj.getString("time") + " - " + obj.getString("content").split("\n")[0].substring(0, Math.min(20, obj.getString("content").split("\n")[0].length())) + "...");
                contents.add(obj.getString("content"));
            }
        } catch (Exception e) {
            e.printStackTrace();
        }

        if (items.isEmpty()) {
            Toast.makeText(this, "暂无历史记录", Toast.LENGTH_SHORT).show();
            return;
        }

        new AlertDialog.Builder(this)
                .setTitle("📋 历史记录 (点击调用)")
                .setAdapter(new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, items), (dialog, which) -> {
                    etCookie.setText(contents.get(which));
                    setMsg("✅ 已从历史记录调用 (未保存)", true);
                })
                .setNegativeButton("清空", (dialog, which) -> {
                    prefs.edit().remove(KEY_HISTORY).apply();
                    Toast.makeText(this, "已清空历史记录", Toast.LENGTH_SHORT).show();
                })
                .setNeutralButton("取消", null)
                .show();
    }

    private void backupToLocal() {
        String content = etCookie.getText().toString().trim();
        if (content.isEmpty()) {
            setMsg("⚠️ 内容为空，无需备份", false);
            return;
        }
        executor.execute(() -> {
            try {
                File dir = new File(Environment.getExternalStorageDirectory(), AppConfig.CONF_DIR_NAME);
                if (!dir.exists()) dir.mkdirs();
                File file = new File(dir, AppConfig.COOKIE_BACKUP_FILE);
                
                FileOutputStream fos = new FileOutputStream(file);
                fos.write(content.getBytes());
                fos.close();
                
                handler.post(() -> {
                    Toast.makeText(this, "✅ 已成功备份到: " + AppConfig.CONF_DIR_NAME + "/" + AppConfig.COOKIE_BACKUP_FILE, Toast.LENGTH_LONG).show();
                    setMsg("✅ 备份成功", true);
                });
            } catch (Exception e) {
                handler.post(() -> setMsg("❌ 备份失败: " + e.getMessage(), false));
            }
        });
    }

    private void restoreFromLocal() {
        executor.execute(() -> {
            try {
                File dir = new File(Environment.getExternalStorageDirectory(), AppConfig.CONF_DIR_NAME);
                File file = new File(dir, AppConfig.COOKIE_BACKUP_FILE);
                if (!file.exists()) {
                    handler.post(() -> setMsg("❌ 本地备份文件不存在", false));
                    return;
                }
                
                FileInputStream fis = new FileInputStream(file);
                BufferedReader reader = new BufferedReader(new InputStreamReader(fis));
                StringBuilder sb = new StringBuilder();
                String line;
                while ((line = reader.readLine()) != null) {
                    sb.append(line).append("\n");
                }
                reader.close();
                fis.close();
                
                String content = sb.toString().trim();
                handler.post(() -> {
                    etCookie.setText(content);
                    Toast.makeText(this, "✅ 已从本地加载备份", Toast.LENGTH_SHORT).show();
                    setMsg("✅ 恢复成功 (未保存到应用)", true);
                });
            } catch (Exception e) {
                handler.post(() -> setMsg("❌ 恢复失败: " + e.getMessage(), false));
            }
        });
    }

    private void setMsg(String msg, boolean ok) {
        tvMsg.setText(msg);
        tvMsg.setTextColor(ok ? 0xFF2ECC71 : 0xFFE74C3C);
    }
}
