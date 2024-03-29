# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-26 12:13
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import jsonfield.fields
import model_utils.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Charge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('stripe_id', models.CharField(max_length=50, unique=True)),
                ('card_last_4', models.CharField(blank=True, max_length=4)),
                ('card_kind', models.CharField(blank=True, max_length=50)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=7, null=True)),
                ('amount_refunded', models.DecimalField(decimal_places=2, max_digits=7, null=True)),
                ('description', models.TextField(blank=True)),
                ('paid', models.NullBooleanField()),
                ('disputed', models.NullBooleanField()),
                ('refunded', models.NullBooleanField()),
                ('captured', models.NullBooleanField()),
                ('fee', models.DecimalField(decimal_places=2, max_digits=7, null=True)),
                ('receipt_sent', models.BooleanField(default=False)),
                ('charge_created', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CurrentSubscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('plan', models.CharField(max_length=100)),
                ('quantity', models.IntegerField()),
                ('start', models.DateTimeField()),
                ('status', models.CharField(max_length=25)),
                ('cancel_at_period_end', models.BooleanField(default=False)),
                ('canceled_at', models.DateTimeField(blank=True, null=True)),
                ('current_period_end', models.DateTimeField(null=True)),
                ('current_period_start', models.DateTimeField(null=True)),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('trial_end', models.DateTimeField(blank=True, null=True)),
                ('trial_start', models.DateTimeField(blank=True, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=7)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('stripe_id', models.CharField(max_length=50, unique=True)),
                ('card_fingerprint', models.CharField(blank=True, max_length=200)),
                ('card_last_4', models.CharField(blank=True, max_length=4)),
                ('card_kind', models.CharField(blank=True, max_length=50)),
                ('card_exp_month', models.PositiveIntegerField(blank=True, null=True)),
                ('card_exp_year', models.PositiveIntegerField(blank=True, null=True)),
                ('date_purged', models.DateTimeField(editable=False, null=True)),
                ('subscriber', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('stripe_id', models.CharField(max_length=50, unique=True)),
                ('livemode', models.BooleanField(default=False)),
                ('kind', models.CharField(max_length=250)),
                ('webhook_message', jsonfield.fields.JSONField()),
                ('validated_message', jsonfield.fields.JSONField(null=True)),
                ('valid', models.NullBooleanField()),
                ('processed', models.BooleanField(default=False)),
                ('customer', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='djstripe.Customer')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EventProcessingException',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('data', models.TextField()),
                ('message', models.CharField(max_length=500)),
                ('traceback', models.TextField()),
                ('event', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='djstripe.Event')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('stripe_id', models.CharField(max_length=50, unique=True)),
                ('attempted', models.NullBooleanField()),
                ('attempts', models.PositiveIntegerField(null=True)),
                ('closed', models.BooleanField(default=False)),
                ('paid', models.BooleanField(default=False)),
                ('period_end', models.DateTimeField()),
                ('period_start', models.DateTimeField()),
                ('subtotal', models.DecimalField(decimal_places=2, max_digits=7)),
                ('total', models.DecimalField(decimal_places=2, max_digits=7)),
                ('date', models.DateTimeField()),
                ('charge', models.CharField(blank=True, max_length=50)),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to='djstripe.Customer')),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='InvoiceItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('stripe_id', models.CharField(max_length=50)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=7)),
                ('currency', models.CharField(max_length=10)),
                ('period_start', models.DateTimeField()),
                ('period_end', models.DateTimeField()),
                ('proration', models.BooleanField(default=False)),
                ('line_type', models.CharField(max_length=50)),
                ('description', models.CharField(blank=True, max_length=200)),
                ('plan', models.CharField(blank=True, max_length=100, null=True)),
                ('quantity', models.IntegerField(null=True)),
                ('invoice', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='djstripe.Invoice')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('stripe_id', models.CharField(max_length=50, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('currency', models.CharField(choices=[('usd', 'U.S. Dollars'), ('gbp', 'Pounds (GBP)'), ('eur', 'Euros')], max_length=10)),
                ('interval', models.CharField(choices=[('week', 'Week'), ('month', 'Month'), ('year', 'Year')], max_length=10, verbose_name='Interval type')),
                ('interval_count', models.IntegerField(default=1, null=True, verbose_name='Intervals between charges')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=7, verbose_name='Amount (per period)')),
                ('trial_period_days', models.IntegerField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Transfer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('stripe_id', models.CharField(max_length=50, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=7)),
                ('status', models.CharField(max_length=25)),
                ('date', models.DateTimeField()),
                ('description', models.TextField(blank=True, null=True)),
                ('adjustment_count', models.IntegerField()),
                ('adjustment_fees', models.DecimalField(decimal_places=2, max_digits=7)),
                ('adjustment_gross', models.DecimalField(decimal_places=2, max_digits=7)),
                ('charge_count', models.IntegerField()),
                ('charge_fees', models.DecimalField(decimal_places=2, max_digits=7)),
                ('charge_gross', models.DecimalField(decimal_places=2, max_digits=7)),
                ('collected_fee_count', models.IntegerField()),
                ('collected_fee_gross', models.DecimalField(decimal_places=2, max_digits=7)),
                ('net', models.DecimalField(decimal_places=2, max_digits=7)),
                ('refund_count', models.IntegerField()),
                ('refund_fees', models.DecimalField(decimal_places=2, max_digits=7)),
                ('refund_gross', models.DecimalField(decimal_places=2, max_digits=7)),
                ('validation_count', models.IntegerField()),
                ('validation_fees', models.DecimalField(decimal_places=2, max_digits=7)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transfers', to='djstripe.Event')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TransferChargeFee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=7)),
                ('application', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('kind', models.CharField(max_length=150)),
                ('transfer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='charge_fee_details', to='djstripe.Transfer')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='currentsubscription',
            name='customer',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='current_subscription', to='djstripe.Customer'),
        ),
        migrations.AddField(
            model_name='charge',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='charges', to='djstripe.Customer'),
        ),
        migrations.AddField(
            model_name='charge',
            name='invoice',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='charges', to='djstripe.Invoice'),
        ),
    ]
