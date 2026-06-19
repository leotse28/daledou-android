package com.daledou;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.widget.Button;
import android.widget.FrameLayout;
import androidx.appcompat.app.AppCompatActivity;

public class ConfigMainActivity extends AppCompatActivity {

    private DefaultConfigPanel defaultPanel;
    private AccountConfigPanel accountPanel;
    private TaskRegisterPanel taskPanel;

    private Button btnTabDefault, btnTabAccount, btnTabTask;
    private FrameLayout container;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_config_main);

        container    = findViewById(R.id.contentFrame);
        btnTabDefault = findViewById(R.id.tabDefault);
        btnTabAccount = findViewById(R.id.tabAccount);
        btnTabTask    = findViewById(R.id.tabTasks);

        findViewById(R.id.btnBack).setOnClickListener(v -> finish());

        btnTabDefault.setOnClickListener(v -> showTab(0));
        btnTabAccount.setOnClickListener(v -> showTab(1));
        btnTabTask.setOnClickListener(v -> showTab(2));

        showTab(0);
    }

    private void showTab(int tab) {
        container.removeAllViews();
        updateTabStyle(tab);

        LayoutInflater inflater = LayoutInflater.from(this);
        switch (tab) {
            case 0: {
                View v = inflater.inflate(R.layout.fragment_default_config, container, false);
                container.addView(v);
                defaultPanel = new DefaultConfigPanel(this, v);
                defaultPanel.onShow();
                break;
            }
            case 1: {
                View v = inflater.inflate(R.layout.fragment_account_config, container, false);
                container.addView(v);
                accountPanel = new AccountConfigPanel(this, v);
                accountPanel.onShow();
                break;
            }
            case 2: {
                View v = inflater.inflate(R.layout.fragment_task_register, container, false);
                container.addView(v);
                taskPanel = new TaskRegisterPanel(this, v);
                taskPanel.onShow();
                break;
            }
        }
    }

    private void updateTabStyle(int active) {
        Button[] tabs = {btnTabDefault, btnTabAccount, btnTabTask};
        for (int i = 0; i < tabs.length; i++) {
            tabs[i].setBackgroundResource(i == active
                ? R.drawable.bg_tab_selected : R.drawable.bg_tab_normal);
            tabs[i].setTextColor(i == active ? 0xFF4FC3F7 : 0xFF9E9E9E);
        }
    }
}
