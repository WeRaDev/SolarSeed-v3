-- Normalize compatibility defaults on res_company.
-- Purpose: when Enterprise addon code is unavailable but Enterprise schema columns exist,
-- inserts on res.company may fail on NOT NULL columns lacking DB defaults.
-- This patch is idempotent and targets known enterprise-related columns that can block inserts.

BEGIN;

DO $$
DECLARE
    rec RECORD;
    chosen_default text;
BEGIN
    FOR rec IN
        SELECT c.column_name
        FROM information_schema.columns c
        WHERE c.table_schema = 'public'
          AND c.table_name = 'res_company'
          AND c.is_nullable = 'NO'
          AND (
                c.column_name LIKE 'generate_deferred_%_method'
             OR c.column_name LIKE 'deferred_%_amount_computation_method'
             OR c.column_name IN (
                    'account_return_periodicity',
                    'account_return_reminder_day',
                    'currency_interval_unit',
                    'timesheet_mail_employee_interval',
                    'timesheet_mail_interval'
                )
          )
    LOOP
        EXECUTE format(
            'SELECT %I::text
             FROM res_company
             WHERE %I IS NOT NULL
             GROUP BY 1
             ORDER BY count(*) DESC, 1
             LIMIT 1',
            rec.column_name,
            rec.column_name
        )
        INTO chosen_default;

        IF chosen_default IS NULL OR chosen_default = '' THEN
            chosen_default := CASE rec.column_name
                WHEN 'generate_deferred_expense_entries_method' THEN 'on_validation'
                WHEN 'generate_deferred_revenue_entries_method' THEN 'on_validation'
                WHEN 'deferred_expense_amount_computation_method' THEN 'month'
                WHEN 'deferred_revenue_amount_computation_method' THEN 'month'
                WHEN 'account_return_periodicity' THEN 'year'
                WHEN 'account_return_reminder_day' THEN '7'
                WHEN 'currency_interval_unit' THEN 'manually'
                WHEN 'timesheet_mail_employee_interval' THEN 'weeks'
                WHEN 'timesheet_mail_interval' THEN 'weeks'
                ELSE 'on_validation'
            END;
        END IF;

        EXECUTE format(
            'UPDATE res_company
             SET %I = %L
             WHERE %I IS NULL',
            rec.column_name,
            chosen_default,
            rec.column_name
        );

        EXECUTE format(
            'ALTER TABLE res_company
             ALTER COLUMN %I SET DEFAULT %L',
            rec.column_name,
            chosen_default
        );
    END LOOP;
END $$;

COMMIT;
