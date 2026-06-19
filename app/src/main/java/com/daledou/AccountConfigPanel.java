package com.daledou;

import android.content.Context;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.TextView;

import com.chaquo.python.PyObject;
import com.chaquo.python.Python;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class AccountConfigPanel {

    private final Context ctx;
    private final Spinner spinnerQQ;
    private final EditText etConfig;
    private final TextView tvMsg;
    private final ExecutorService executor = Executors.newSingleThreadExecutor();
    private final Handler handler = new Handler(Looper.getMainLooper());
    private List<String> qqList = new ArrayList<>();
    private String currentQQ = null;

    public AccountConfigPanel(Context ctx, View root) {
        this.ctx = ctx;
        spinnerQQ = root.findViewById(R.id.spinnerQQ);
        etConfig  = root.findViewById(R.id.etAccountConfig);
        tvMsg     = root.findViewById(R.id.tvAccountMsg);

        root.findViewById(R.id.btnSaveAccount).setOnClickListener(v -> save());
        root.findViewById(R.id.btnCopyFromDefault).setOnClickListener(v -> copyFromDefault());

        spinnerQQ.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override public void onItemSelected(AdapterView<?> parent, View view, int position, long id) {
                if (position >= 0 && position < qqList.size()) {
                    currentQQ = qqList.get(position);
                    loadAccount(currentQQ);
                }
            }
            @Override public void onNothingSelected(AdapterView<?> parent) {}
        });
    }

    public void onShow() {
        loadQQList();
    }

    private void loadQQList() {
        executor.execute(() -> {
            try {
                PyObject bridge = Python.getInstance().getModule("bridge");
                String raw = bridge.callAttr("get_qq_list").toString();
                List<String> list = new ArrayList<>();
                if (!raw.isEmpty()) {
                    for (String s : raw.split(",")) {
                        String q = s.trim();
                        if (!q.isEmpty()) list.add(q);
                    }
                }
                handler.post(() -> {
                    qqList = list;
                    if (list.isEmpty()) {
                        list.add("(无账号，请先配置Cookie)");
                    }
                    ArrayAdapter<String> adapter = new ArrayAdapter<>(ctx,
                        android.R.layout.simple_spinner_item, list);
                    adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);
                    spinnerQQ.setAdapter(adapter);
                });
            } catch (Exception e) {
                handler.post(() -> setMsg("❌ 加载账号列表失败: " + e.getMessage(), false));
            }
        });
    }

    private void loadAccount(String qq) {
        executor.execute(() -> {
            try {
                PyObject bridge = Python.getInstance().getModule("bridge");
                String content = bridge.callAttr("load_account_config", qq).toString();
                handler.post(() -> {
                    etConfig.setText(content);
                    setMsg("✅ 已加载账号 " + qq + " 的配置", true);
                });
            } catch (Exception e) {
                handler.post(() -> setMsg("❌ 加载失败: " + e.getMessage(), false));
            }
        });
    }

    private void save() {
        if (currentQQ == null || currentQQ.startsWith("(")) {
            setMsg("⚠️ 请先选择有效账号", false);
            return;
        }
        String content = etConfig.getText().toString();
        executor.execute(() -> {
            try {
                PyObject bridge = Python.getInstance().getModule("bridge");
                bridge.callAttr("save_account_config", currentQQ, content);
                handler.post(() -> setMsg("✅ 账号 " + currentQQ + " 配置已保存", true));
            } catch (Exception e) {
                handler.post(() -> setMsg("❌ 保存失败: " + e.getMessage(), false));
            }
        });
    }

    private void copyFromDefault() {
        executor.execute(() -> {
            try {
                PyObject bridge = Python.getInstance().getModule("bridge");
                String content = bridge.callAttr("load_default_config").toString();
                handler.post(() -> {
                    etConfig.setText(content);
                    setMsg("✅ 已复制默认配置，可修改后保存", true);
                });
            } catch (Exception e) {
                handler.post(() -> setMsg("❌ 复制失败: " + e.getMessage(), false));
            }
        });
    }

    private void setMsg(String msg, boolean ok) {
        tvMsg.setText(msg);
        tvMsg.setTextColor(ok ? 0xFF2ECC71 : 0xFFE74C3C);
    }
}
