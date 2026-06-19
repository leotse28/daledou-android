package com.daledou;

import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class CookieActivity extends AppCompatActivity {

    private EditText etCookie;
    private TextView tvMsg;
    private final ExecutorService executor = Executors.newSingleThreadExecutor();
    private final Handler handler = new Handler(Looper.getMainLooper());

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_cookie);

        etCookie = findViewById(R.id.etCookie);
        tvMsg    = findViewById(R.id.tvMsg);
        Button btnBack = findViewById(R.id.btnBack);
        Button btnSave = findViewById(R.id.btnSave);
        Button btnLoad = findViewById(R.id.btnLoad);

        btnBack.setOnClickListener(v -> finish());
        btnSave.setOnClickListener(v -> save());
        btnLoad.setOnClickListener(v -> load());

        load();
    }

    private void load() {
        executor.execute(() -> {
            try {
                PyObject bridge = Python.getInstance().getModule("bridge");
                String content = bridge.callAttr("get_cookie_yaml").toString();
                handler.post(() -> {
                    etCookie.setText(content);
                    setMsg("✅ 已加载 Cookie 配置", true);
                });
            } catch (Exception e) {
                handler.post(() -> setMsg("❌ 加载失败: " + e.getMessage(), false));
            }
        });
    }

    private void save() {
        String content = etCookie.getText().toString().trim();
        if (content.isEmpty()) {
            setMsg("⚠️ 内容不能为空", false);
            return;
        }
        executor.execute(() -> {
            try {
                PyObject bridge = Python.getInstance().getModule("bridge");
                bridge.callAttr("save_cookies", content);
                handler.post(() -> setMsg("✅ Cookie 已保存", true));
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
