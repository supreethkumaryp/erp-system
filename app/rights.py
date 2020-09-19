from app.schema import roles
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for, jsonify

rights = {
    url_for("general.branches") : roles["admin"]
}

print(rights)